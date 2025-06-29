import csv
from datetime import datetime
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.utils.dateparse import parse_datetime
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db import transaction
from django.db.models import Count, Sum

from .models import Fish
from core.permissions import IsAdminUser, IsFisher
from user.models import Fisher


# 获取当前用户（渔夫）鱼群的总体状态信息
@api_view(['GET'])
@permission_classes([IsFisher])
def get_my_fish_status(request):
    fisher = get_object_or_404(Fisher, user=request.user)

    # 可选时间参数
    start_time_str = request.query_params.get('start_time')
    end_time_str = request.query_params.get('end_time')
    start_time = parse_datetime(start_time_str) if start_time_str else None
    end_time = parse_datetime(end_time_str) if end_time_str else None

    fish_qs = Fish.objects.filter(fisher_id=fisher)
    if start_time:
        fish_qs = fish_qs.filter(created_at__gte=start_time)
    if end_time:
        fish_qs = fish_qs.filter(created_at__lte=end_time)

    total_fish = fish_qs.count()
    total_weight = fish_qs.aggregate(weight_sum=Sum('weight'))['weight_sum'] or 0
    species_count = fish_qs.values('species').distinct().count()
    new_fish = fish_qs.filter(created_at__gte=start_time).count() if start_time else 0
    has_is_alive = any(f.name == 'is_alive' for f in Fish._meta.fields)
    dead_fish = fish_qs.filter(is_alive=False).count() if has_is_alive else 0

    return Response({
        'total_fish': total_fish,
        'total_weight': total_weight,
        'species_count': species_count,
        'new_fish': new_fish,
        'dead_fish': dead_fish,
    }, status=status.HTTP_200_OK)


# 获取所有鱼群的总体信息
@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_all_fish_status(request):
    start_time_str = request.query_params.get('start_time')
    end_time_str = request.query_params.get('end_time')

    fish_qs = Fish.objects.all()

    # 时间筛选
    if start_time_str:
        start_time = parse_datetime(start_time_str)
        if start_time:
            fish_qs = fish_qs.filter(added_at__gte=start_time)
    else:
        start_time = None

    if end_time_str:
        end_time = parse_datetime(end_time_str)
        if end_time:
            fish_qs = fish_qs.filter(added_at__lte=end_time)

    total_fish = fish_qs.count()
    total_weight = fish_qs.aggregate(weight_sum=Sum('weight'))['weight_sum'] or 0

    # 每种品种的数量与总重
    species_stats = fish_qs.values('species').annotate(
        count=Count('id'),
        weight=Sum('weight')
    )

    # 新增数量（按起始时间）
    new_fish = fish_qs.filter(added_at__gte=start_time).count() if start_time else 0

    # 死亡数量（is_alive=False）
    dead_fish = fish_qs.filter(is_alive=False).count()

    return Response({
        'total_fish': total_fish,
        'total_weight': total_weight,
        'species_details': list(species_stats),
        'new_fish': new_fish,
        'dead_fish': dead_fish,
    }, status=status.HTTP_200_OK)


# 获取当前渔民的所有鱼数据详细列表
@api_view(['GET'])
@permission_classes([IsFisher])
def get_fish_list(request):
    fisher = get_object_or_404(Fisher, user=request.user)
    fish_list = Fish.objects.filter(fisher_id=fisher)
    data = [{
        'fisher_id': fish.fisher.id,
        'species': fish.species,
        'weight': fish.weight,
        'length1': fish.length1,
        'length2': fish.length2,
        'length3': fish.length3,
        'height': fish.height,
        'width': fish.width,
    } for fish in fish_list]
    return Response({'fish_group': data}, status=status.HTTP_200_OK)


# 获取所有鱼的详细数据列表
@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_all_fish_list(request):
    fisher = get_object_or_404(Fisher, user=request.user)
    fish_list = Fish.objects.filter(fisher_id=fisher)
    data = [{
        'fisher_id': fish.fisher.id,
        'species': fish.species,
        'weight': fish.weight,
        'length1': fish.length1,
        'length2': fish.length2,
        'length3': fish.length3,
        'height': fish.height,
        'width': fish.width,
    } for fish in fish_list]
    return Response({'fish_group': data}, status=status.HTTP_200_OK)



# 上传数据
@api_view(['POST'])
@permission_classes([IsFisher])
def upload_fish_csv(request):    
    # 获取并验证 fisher_id
    try:
        fisher_id = int(request.data.get("fisher_id"))
    except (ValueError, TypeError):
        return Response({'error': 'fisher_id 必须是有效的整数'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not fisher_id:
        return Response({'error': '缺少 fisher_id 参数'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 获取并验证csv数据文件
    if 'file' not in request.FILES:
        return Response({'error': '未上传文件'}, status=status.HTTP_400_BAD_REQUEST)
    
    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        return Response({'error': '请上传 CSV 文件'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        
        # 验证表头
        required_fields = {'species', 'weight', 'length1'}
        if not required_fields.issubset(reader.fieldnames):
            missing = required_fields - set(reader.fieldnames)
            return Response({'error': f'缺少必要字段: {", ".join(missing)}'}, status=400)
        
        fish_instances = []
        errors = []
        
        with transaction.atomic():
            for i, row in enumerate(reader, start=2):  # 从第2行开始
                try:                    
                    # 创建鱼对象
                    fish = Fish(
                        fisher_id=fisher_id,
                        species=row['species'],
                        weight=float(row['weight']),
                        length1=float(row['length1']),
                        length2=float(row.get('length2', 0)),
                        length3=float(row.get('length3', 0)),
                        height=float(row.get('height', 0)),
                        width=float(row.get('width', 0)),
                        is_alive=row.get('is_alive', 'True').lower() == 'true',
                    )
                    
                    # 可选字段处理
                    if row.get('died_at'):
                        fish.died_at = datetime.fromisoformat(row['died_at'])
                    
                    fish_instances.append(fish)
                except Fisher.DoesNotExist:
                    errors.append(f'第 {i} 行：渔民账号 {row["fisher_account"]} 不存在')
                except Exception as e:
                    errors.append(f'第 {i} 行：{str(e)}')
        
        if errors:
            return Response({'errors': errors}, status=400)
        
        Fish.objects.bulk_create(fish_instances)
        return Response({'message': f'成功导入 {len(fish_instances)} 条记录'}, status=201)
    
    except UnicodeDecodeError:
        return Response({'error': '文件编码错误，确保使用 UTF-8'}, status=400)
    

# 下载鱼类数据
@api_view(['GET'])
@permission_classes([IsFisher])
def download_fish_csv(request):
    # 获取 fisher_id
    fisher_id = request.user.fisher.id
    
    # 创建响应对象，设置为 CSV 格式
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="fish_data.csv"'
    
    # 创建 CSV 写入器
    writer = csv.writer(response)
    
    # 写入表头
    writer.writerow([
        'id', 'fisher_account', 'species', 'weight', 'length1', 
        'length2', 'length3', 'height', 'width', 'is_alive', 'died_at'
    ])
    
    # 查询并写入数据
    fish_data = Fish.objects.select_related('fisher').filter(fisher_id=fisher_id)
    
    for fish in fish_data:
        writer.writerow([
            fish.id,
            fish.fisher.id,
            fish.species,
            fish.weight,
            fish.length1,
            fish.length2,
            fish.length3,
            fish.height,
            fish.width,
            fish.is_alive,
            fish.died_at.isoformat() if fish.died_at else '',
        ])
    
    return response


# 下载所有鱼类数据
@api_view(['GET'])
@permission_classes([IsAdminUser])
def download_all_fish_csv(request):        
    # 创建响应对象，设置为 CSV 格式
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="fish_data.csv"'
    
    # 创建 CSV 写入器
    writer = csv.writer(response)
    
    # 写入表头
    writer.writerow([
        'id', 'fisher_account', 'species', 'weight', 'length1', 
        'length2', 'length3', 'height', 'width', 'is_alive', 'died_at'
    ])
    
    # 查询并写入数据
    fish_data = Fish.objects.select_related('fisher').all()
    
    for fish in fish_data:
        writer.writerow([
            fish.id,
            fish.fisher.id,
            fish.species,
            fish.weight,
            fish.length1,
            fish.length2,
            fish.length3,
            fish.height,
            fish.width,
            fish.is_alive,
            fish.died_at.isoformat() if fish.died_at else '',
        ])
    
    return response