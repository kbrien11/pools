from django.contrib import admin
from django.contrib.auth.models import User



from .models import Board,Box,NFL,Winnings,MarchMadness,Admin


admin.site.register(Board)
admin.site.register(Box)
admin.site.register(NFL)
admin.site.register(Winnings)
admin.site.register(MarchMadness)
admin.site.register(Admin)

