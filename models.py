from django.db import models
from user.models import Fisher
from django.utils import timezone


class Fish(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="鱼ID")
    fisher = models.ForeignKey(Fisher, on_delete=models.CASCADE, db_index=True, verbose_name="渔民ID")
    species = models.CharField(max_length=100, verbose_name="物种")
    weight = models.FloatField(verbose_name="重量（克）")
    length1 = models.FloatField(verbose_name="长度1（厘米）")
    length2 = models.FloatField(verbose_name="长度2（厘米）")
    length3 = models.FloatField(verbose_name="长度3（厘米）")
    height = models.FloatField(verbose_name="高度（厘米）")
    width = models.FloatField(verbose_name="宽度（厘米）")
    added_at = models.DateTimeField(default=timezone.now, db_index=True, verbose_name="添加时间")
    is_alive = models.BooleanField(default=True, db_index=True, verbose_name="是否存活")
    died_at = models.DateTimeField(null=True, blank=True, verbose_name="死亡时间")

    def __str__(self):
        return self.species

# 修改2