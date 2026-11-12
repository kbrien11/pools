import random
import secrets
import string

from decimal import Decimal, InvalidOperation

from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from django.db.models import Sum, Count, Q
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import (
    Board,
    Box,
    NFL,
    MarchMadness,
    Winnings,
    Admin,
    GeneratedNumbers,
)

from .serializers import (
    BoardSerializer,
    BoxSerializer,
    NFLSerializer,
    MarchMadnessSerializer,
    WinningsSerializer,
    AdminSerializer,
    GeneratedNumbersSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()


# ---------------------------------------------------------
# AUTHENTICATION
# ---------------------------------------------------------

@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.save()
    token, _ = Token.objects.get_or_create(user=user)

    print(user)
    print(token)

    return Response(
        {
            "token": token.key,
            "user": UserSerializer(user).data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get("email", "").strip().lower()
    password = request.data.get("password", "")

    if not email or not password:
        return Response(
            {"error": "Email and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = User.objects.filter(email__iexact=email).first()

    if user is None:
        return Response(
            {"error": "Invalid email or password."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    authenticated_user = authenticate(
        request,
        username=user.get_username(),
        password=password,
    )

    if authenticated_user is None:
        return Response(
            {"error": "Invalid email or password."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    token, _ = Token.objects.get_or_create(user=authenticated_user)

    return Response(
        {
            "token": token.key,
            "user": UserSerializer(authenticated_user).data,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    request.auth.delete()
    return Response({"message": "Logged out successfully."})


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def user_is_board_admin(user, board):
    return Admin.objects.filter(
        user_pk=user,
        board_number=board,
    ).exists()


def user_is_board_member(user, board):
    return (
        user_is_board_admin(user, board)
        or Box.objects.filter(
            board_number=board,
            user_pk=user,
        ).exists()
    )


def generate_board_code():
    """
    Generate a unique numeric board code.
    """
    for _ in range(20):
        code = random.randint(1000, 99999)

        if not Board.objects.filter(code=code).exists():
            return code

    # Fallback in the unlikely event of repeated collisions.
    while True:
        code = int("".join(secrets.choice(string.digits) for _ in range(8)))
        if not Board.objects.filter(code=code).exists():
            return code


def get_board_boxes(board):
    return Box.objects.filter(board_number=board).select_related("user_pk")


# ---------------------------------------------------------
# BOARDS / POOLS
# ---------------------------------------------------------

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def pools(request):
    if request.method == "GET":
        admin_board_ids = Admin.objects.filter(
            user_pk=request.user
        ).values_list("board_number_id", flat=True)

        claimed_board_ids = Box.objects.filter(
            user_pk=request.user
        ).values_list("board_number_id", flat=True)

        board_ids = set(admin_board_ids) | set(claimed_board_ids)

        boards = Board.objects.filter(id__in=board_ids).distinct()

        return Response(BoardSerializer(boards, many=True).data)

    name = request.data.get("name", "").strip()
    board_type = request.data.get("type", "").strip().lower()
    box_price = request.data.get("box_price")

    if not name:
        return Response(
            {"error": "A board name is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if board_type not in ["nfl", "marchmadness"]:
        return Response(
            {"error": "Type must be 'nfl' or 'marchmadness'."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        box_price = Decimal(str(box_price))
        if box_price < 0:
            raise InvalidOperation
    except (InvalidOperation, TypeError, ValueError):
        return Response(
            {"error": "A valid non-negative box_price is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    with transaction.atomic():
        board = Board.objects.create(
            name=name,
            type=board_type,
            box_price=box_price,
            code=generate_board_code(),
        )

        Admin.objects.create(
            user_pk=request.user,
            board_number=board,
            creator=True,
        )

        # Create all 100 possible squares: 00 through 99.
        Box.objects.bulk_create(
            [
                Box(
                    board_number=board,
                    pair=f"{number:02d}",
                )
                for number in range(100)
            ]
        )



        if board_type == "nfl":
            NFL.objects.create(
                board_number=board,
                box_price=box_price,
                one=request.data.get("one", 0),
                two=request.data.get("two", 0),
                three=request.data.get("three", 0),
                four=request.data.get("four", 0),
            )
        else:
            MarchMadness.objects.create(
                board_number=board,
                box_price=box_price,
                first_round=request.data.get("first_round", 0),
                second_round=request.data.get("second_round", 0),
                sweet_sixteen=request.data.get("sweet_sixteen", 0),
                elite_eight=request.data.get("elite_eight", 0),
                final_four=request.data.get("final_four", 0),
                championship=request.data.get("championship", 0),
            )

        winning_numbers = list(range(10))
        losing_numbers = list(range(10))

        random.shuffle(winning_numbers)
        random.shuffle(losing_numbers)

        print("keith")

        GeneratedNumbers.objects.update_or_create(
            board_pk=board,
            defaults={
                "winning": winning_numbers,
                "losing": losing_numbers,
            },
        )
        print("keith")
        print(board)

    return Response(
        {
            "board": BoardSerializer(board).data,
            "boxes": BoxSerializer(get_board_boxes(board), many=True).data,
            "winning_numbers": winning_numbers,
            "losing_numbers": losing_numbers,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def pool_detail(request, pool_id):
    board = get_object_or_404(Board, id=pool_id)

    if not user_is_board_member(request.user, board):
        return Response(
            {"error": "You do not have access to this board."},
            status=status.HTTP_403_FORBIDDEN,
        )

    return Response(BoardSerializer(board).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def join_pool(request):
    code = request.data.get("code")

    if not code:
        return Response(
            {"error": "A board code is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    board = Board.objects.filter(code=code).first()

    if board is None:
        return Response(
            {"error": "Board not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # A user becomes a member when they claim a box.
    # This endpoint validates the code and returns the board.
    return Response(
        {
            "board": BoardSerializer(board).data,
            "remaining_boxes": Box.objects.filter(
                board_number=board,
                user_pk__isnull=True,
            ).count(),
        }
    )


# ---------------------------------------------------------
# BOXES
# ---------------------------------------------------------

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def pool_boxes(request, pool_id):
    board = get_object_or_404(Board, id=pool_id)

    if not user_is_board_member(request.user, board):
        return Response(
            {"error": "You do not have access to this board."},
            status=status.HTTP_403_FORBIDDEN,
        )

    boxes = get_board_boxes(board)

    return Response(BoxSerializer(boxes, many=True).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def claim_boxes(request, pool_id):
    board = get_object_or_404(Board, id=pool_id)

    box_ids = request.data.get("box_ids", [])

    if not isinstance(box_ids, list) or not box_ids:
        return Response(
            {"error": "Provide a non-empty box_ids list."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if len(box_ids) != len(set(box_ids)):
        return Response(
            {"error": "Duplicate box IDs were provided."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    with transaction.atomic():
        # Lock the requested rows so simultaneous claims cannot
        # successfully claim the same boxes.
        boxes = list(
            Box.objects.select_for_update().filter(
                id__in=box_ids,
                board_number=board,
            )
        )

        if len(boxes) != len(box_ids):
            return Response(
                {"error": "One or more boxes were not found on this board."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if any(box.user_pk_id is not None for box in boxes):
            return Response(
                {"error": "One or more boxes have already been claimed."},
                status=status.HTTP_409_CONFLICT,
            )

        for box in boxes:
            box.user_pk = request.user
            box.username = request.user.username
            box.first_name = request.user.first_name

        Box.objects.bulk_update(
            boxes,
            ["user_pk", "username", "first_name"],
        )

    return Response(
        {
            "message": "Boxes claimed successfully.",
            "boxes": BoxSerializer(boxes, many=True).data,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def verify_box(request, pool_id, box_id):
    board = get_object_or_404(Board, id=pool_id)

    box = get_object_or_404(
        Box,
        id=box_id,
        board_number=board,
    )

    return Response(
        {
            "available": box.user_pk_id is None,
            "box": BoxSerializer(box).data,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def remaining_boxes(request, pool_id):
    board = get_object_or_404(Board, id=pool_id)

    if not user_is_board_member(request.user, board):
        return Response(
            {"error": "You do not have access to this board."},
            status=status.HTTP_403_FORBIDDEN,
        )

    remaining = Box.objects.filter(
        board_number=board,
        user_pk__isnull=True,
    ).count()

    return Response({"remaining_boxes": remaining})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def pool_status(request, pool_id):
    board = get_object_or_404(Board, id=pool_id)

    if not user_is_board_member(request.user, board):
        return Response(
            {"error": "You do not have access to this board."},
            status=status.HTTP_403_FORBIDDEN,
        )

    total = Box.objects.filter(board_number=board).count()
    claimed = Box.objects.filter(
        board_number=board,
        user_pk__isnull=False,
    ).count()

    return Response(
        {
            "total_boxes": total,
            "claimed_boxes": claimed,
            "remaining_boxes": total - claimed,
            "game_in_progress": claimed > 0,
            "is_full": total > 0 and claimed == total,
        }
    )


# ---------------------------------------------------------
# LEADERBOARD / WINNINGS
# ---------------------------------------------------------

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def leaderboard(request, pool_id):
    board = get_object_or_404(Board, id=pool_id)

    if not user_is_board_member(request.user, board):
        return Response(
            {"error": "You do not have access to this board."},
            status=status.HTTP_403_FORBIDDEN,
        )

    winnings = Winnings.objects.filter(
        board_pk=board,
    ).select_related("user_pk").order_by("-balance")

    return Response(WinningsSerializer(winnings, many=True).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_winnings(request, pool_id):
    board = get_object_or_404(Board, id=pool_id)

    winnings = Winnings.objects.filter(
        board_pk=board,
        user_pk=request.user,
    )

    return Response(WinningsSerializer(winnings, many=True).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def money_owed(request, pool_id):
    board = get_object_or_404(Board, id=pool_id)

    if not user_is_board_admin(request.user, board):
        return Response(
            {"error": "Only board admins can view this information."},
            status=status.HTTP_403_FORBIDDEN,
        )

    total_owed = Box.objects.filter(
        board_number=board,
        user_pk__isnull=False,
    ).aggregate(total=Sum("balance"))["total"] or Decimal("0.00")

    return Response({"money_owed": str(total_owed)})


# ---------------------------------------------------------
# BOARD ADMIN / CONFIGURATION
# ---------------------------------------------------------

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def validate_creator(request, pool_id):
    board = get_object_or_404(Board, id=pool_id)

    return Response(
        {"is_creator": Admin.objects.filter(
            user_pk=request.user,
            board_number=board,
            creator=True,
        ).exists()}
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_board_numbers(request, pool_id):
    board = get_object_or_404(Board, id=pool_id)

    if not user_is_board_member(request.user, board):
        return Response(
            {"error": "You do not have access to this board."},
            status=status.HTTP_403_FORBIDDEN,
        )

    numbers = get_object_or_404(GeneratedNumbers, board_pk=board)

    return Response(GeneratedNumbersSerializer(numbers).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_board_payout(request, pool_id):
    board = get_object_or_404(Board, id=pool_id)

    if not user_is_board_member(request.user, board):
        return Response(
            {"error": "You do not have access to this board."},
            status=status.HTTP_403_FORBIDDEN,
        )

    if board.type == "nfl":
        payout = get_object_or_404(NFL, board_number=board)
        return Response(NFLSerializer(payout).data)

    payout = get_object_or_404(MarchMadness, board_number=board)
    return Response(MarchMadnessSerializer(payout).data)