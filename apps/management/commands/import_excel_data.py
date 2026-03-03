#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Excel数据导入命令
将Excel文件数据导入到数据库表中

使用方法:
    python manage.py import_excel_data --attractions tests/景点集合信息.xlsx --restaurants tests/餐厅集合信息.xlsx
    python manage.py import_excel_data --attractions tests/景点集合信息.xlsx
    python manage.py import_excel_data --restaurants tests/餐厅集合信息.xlsx
"""
import os
import sys
import json
import uuid
import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Any, Tuple, Optional

import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ValidationError

from apps.models import Attraction, Restaurant, Hotel

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ImportReport:
    """导入报告类"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.end_time = None
        self.records_total = 0
        self.records_success = 0
        self.records_failed = 0
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
    
    def add_error(self, record_index: int, field: str, value: Any, reason: str):
        """添加错误记录"""
        self.errors.append({
            'record_index': record_index,
            'field': field,
            'value': value,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        })
        self.records_failed += 1
    
    def add_warning(self, record_index: int, field: str, value: Any, reason: str):
        """添加警告记录"""
        self.warnings.append({
            'record_index': record_index,
            'field': field,
            'value': value,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        })
    
    def add_success(self):
        """添加成功记录"""
        self.records_success += 1
    
    def finalize(self):
        """完成报告"""
        self.end_time = datetime.now()
    
    def _serialize_value(self, value: Any) -> Any:
        """序列化值，确保可以被JSON序列化"""
        import datetime
        if isinstance(value, (datetime.datetime, datetime.date)):
            return value.isoformat()
        elif isinstance(value, datetime.time):
            return value.strftime('%H:%M:%S')
        elif isinstance(value, (list, tuple)):
            return [self._serialize_value(item) for item in value]
        elif isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        elif value is None:
            return None
        elif pd.isna(value):
            return None
        else:
            try:
                import json
                json.dumps(value)
                return value
            except:
                return str(value)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        # 序列化错误记录
        serialized_errors = []
        for error in self.errors:
            serialized_error = error.copy()
            serialized_error['value'] = self._serialize_value(error['value'])
            serialized_errors.append(serialized_error)
        
        # 序列化警告记录
        serialized_warnings = []
        for warning in self.warnings:
            serialized_warning = warning.copy()
            serialized_warning['value'] = self._serialize_value(warning['value'])
            serialized_warnings.append(serialized_warning)
        
        return {
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': (self.end_time - self.start_time).total_seconds() if self.end_time else None,
            'records_total': self.records_total,
            'records_success': self.records_success,
            'records_failed': self.records_failed,
            'success_rate': f"{(self.records_success / self.records_total * 100):.2f}%" if self.records_total > 0 else "0%",
            'errors': serialized_errors,
            'warnings': serialized_warnings
        }
    
    def to_text(self) -> str:
        """生成文本报告"""
        lines = [
            "=" * 60,
            "数据导入报告",
            "=" * 60,
            f"开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"结束时间: {self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else 'N/A'}",
        ]
        
        if self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
            lines.append(f"耗时: {duration:.2f} 秒")
        
        lines.extend([
            "-" * 60,
            "统计信息:",
            f"  总记录数: {self.records_total}",
            f"  成功导入: {self.records_success}",
            f"  失败记录: {self.records_failed}",
            f"  成功率: {(self.records_success / self.records_total * 100):.2f}%" if self.records_total > 0 else "  成功率: 0%",
            "-" * 60,
        ])
        
        if self.errors:
            lines.extend([
                "错误详情:",
                "-" * 60,
            ])
            for i, error in enumerate(self.errors[:20], 1):  # 只显示前20个错误
                lines.append(f"  {i}. 记录 #{error['record_index']}, 字段 '{error['field']}'")
                lines.append(f"     值: {error['value']}")
                lines.append(f"     原因: {error['reason']}")
                lines.append("")
            if len(self.errors) > 20:
                lines.append(f"  ... 还有 {len(self.errors) - 20} 个错误未显示")
        
        if self.warnings:
            lines.extend([
                "-" * 60,
                "警告详情:",
                "-" * 60,
            ])
            for i, warning in enumerate(self.warnings[:10], 1):  # 只显示前10个警告
                lines.append(f"  {i}. 记录 #{warning['record_index']}, 字段 '{warning['field']}'")
                lines.append(f"     值: {warning['value']}")
                lines.append(f"     原因: {warning['reason']}")
                lines.append("")
            if len(self.warnings) > 10:
                lines.append(f"  ... 还有 {len(self.warnings) - 10} 个警告未显示")
        
        lines.append("=" * 60)
        return "\n".join(lines)


class ExcelDataReader:
    """Excel数据读取器"""
    
    @staticmethod
    def read_excel(file_path: str) -> List[Dict[str, Any]]:
        """
        读取Excel文件并解析为记录列表
        
        支持三种Excel格式:
        1. 转置结构：前4行是元数据，从第5行开始是字段名，每列代表一条记录
        2. 标准结构：第一行是字段名，每行代表一条记录
        3. 酒店专用结构：前2行是表头，从第3行开始，第一列是序号，第二列是字段名，第四列是数据
        """
        logger.info(f"读取Excel文件: {file_path}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        try:
            # 读取Excel文件，不指定header
            df = pd.read_excel(file_path, header=None)
            
            # 检查是否是酒店专用结构
            if len(df) > 10 and len(df.columns) >= 4:
                # 检查第二行是否包含字段名称
                second_row = df.iloc[1].tolist()
                if '字段名称' in str(second_row) or '字段名' in str(second_row):
                    # 酒店专用结构解析
                    data_df = df.iloc[2:].copy()  # 从第3行开始
                    field_names = data_df.iloc[:, 1].tolist()  # 第二列是字段名
                    
                    # 检查字段名是否有效
                    valid_field_names = [f for f in field_names if pd.notna(f) and str(f).strip()]
                    
                    if len(valid_field_names) > 10:
                        # 第四列是数据
                        record = {}
                        has_data = False
                        for row_idx, field_name in enumerate(field_names):
                            if pd.notna(field_name) and str(field_name).strip():
                                value = data_df.iloc[row_idx, 3]  # 第四列是数据
                                record[str(field_name).strip()] = value
                                if pd.notna(value) and str(value).strip():
                                    has_data = True
                        
                        if has_data:
                            logger.info(f"成功读取 1 条记录（酒店专用结构）")
                            return [record]
            
            # 检查文件结构
            if len(df) > 4 and len(df.columns) > 4:
                # 尝试转置结构解析
                data_df = df.iloc[4:].copy()
                field_names = data_df.iloc[:, 0].tolist()
                
                # 检查字段名是否有效（不是数字或空值）
                valid_field_names = [f for f in field_names if pd.notna(f) and not str(f).isdigit()]
                
                if len(valid_field_names) > 10:
                    # 转置解析：从第4列开始是数据
                    records = []
                    for col_idx in range(4, len(data_df.columns)):
                        record = {}
                        has_data = False
                        for row_idx, field_name in enumerate(field_names):
                            if pd.notna(field_name):
                                value = data_df.iloc[row_idx, col_idx]
                                record[field_name] = value
                                if pd.notna(value) and str(value).strip():
                                    has_data = True
                        if has_data:
                            records.append(record)
                    
                    if records:
                        logger.info(f"成功读取 {len(records)} 条记录（转置结构）")
                        return records
            
            # 标准结构解析：第一行是字段名，每行代表一条记录
            try:
                # 尝试使用第一行作为header
                df_with_header = pd.read_excel(file_path)
                records = df_with_header.to_dict('records')
                
                # 过滤空记录
                records = [r for r in records if any(pd.notna(v) and str(v).strip() for v in r.values())]
                
                # 过滤表头记录
                filtered_records = []
                for r in records:
                    # 检查是否是表头记录（包含字段名称等关键词）
                    is_header = False
                    for k, v in r.items():
                        if pd.notna(v):
                            if '字段名称' in str(v) or '字段名' in str(v) or '序号' in str(v):
                                is_header = True
                                break
                    if not is_header:
                        filtered_records.append(r)
                
                logger.info(f"成功读取 {len(filtered_records)} 条记录（标准结构）")
                return filtered_records
            except Exception as e:
                logger.debug(f"标准结构解析失败: {e}")
            
            # 如果所有方法都失败，返回空列表
            logger.warning(f"无法解析Excel文件结构: {file_path}")
            return []
            
        except Exception as e:
            logger.error(f"读取Excel文件失败: {e}")
            raise


class DataValidator:
    """数据验证器"""
    
    # 景点状态映射
    ATTRACTION_STATUS_MAP = {
        '营业中': 'ACTIVE',
        '非营业中': 'INACTIVE',
        '建设中': 'UNDER_CONSTRUCTION',
        '已关闭': 'CLOSED',
        'ACTIVE': 'ACTIVE',
        'INACTIVE': 'INACTIVE',
        'UNDER_CONSTRUCTION': 'UNDER_CONSTRUCTION',
        'CLOSED': 'CLOSED',
    }
    
    # 景点分类映射
    ATTRACTION_CATEGORY_MAP = {
        '自然景观': 'NATURAL',
        '历史古迹': 'HISTORICAL',
        '文化景点': 'CULTURAL',
        '宗教场所': 'RELIGIOUS',
        '现代景点': 'MODERN',
        '娱乐场所': 'ENTERTAINMENT',
        '购物场所': 'SHOPPING',
        '户外景点': 'OUTDOOR',
        '室内景点': 'INDOOR',
        '公园': 'NATURAL',
        '科技馆': 'MODERN',
        '人造乐园': 'ENTERTAINMENT',
        '自然+建筑文化': 'CULTURAL',
        '其他': 'OTHER',
    }
    
    # 餐厅状态映射
    RESTAURANT_STATUS_MAP = {
        '营业中': 'ACTIVE',
        '未营业': 'INACTIVE',
        '临时关闭': 'TEMPORARILY_CLOSED',
        '永久关闭': 'PERMANENTLY_CLOSED',
        'ACTIVE': 'ACTIVE',
        'INACTIVE': 'INACTIVE',
        'TEMPORARILY_CLOSED': 'TEMPORARILY_CLOSED',
        'PERMANENTLY_CLOSED': 'PERMANENTLY_CLOSED',
    }
    
    # 酒店类型映射
    HOTEL_TYPE_MAP = {
        '奢华酒店': 'LUXURY',
        '商务酒店': 'BUSINESS',
        '度假酒店': 'RESORT',
        '精品酒店': 'BOUTIQUE',
        '经济酒店': 'ECONOMY',
        '民宿': 'HOMESTAY',
        '其他': 'OTHER'
    }
    
    # 酒店状态映射
    HOTEL_STATUS_MAP = {
        '营业中': 'ACTIVE',
        '未营业': 'INACTIVE',
        '装修中': 'RENOVATING',
        '已关闭': 'CLOSED',
        '其他': 'OTHER',
        'ACTIVE': 'ACTIVE',
        'INACTIVE': 'INACTIVE',
        'RENOVATING': 'RENOVATING',
        'CLOSED': 'CLOSED'
    }
    
    # 餐厅类型映射
    RESTAURANT_TYPE_MAP = {
        '精致餐饮': 'FINE_DINING',
        '休闲餐饮': 'CASUAL',
        '快餐': 'FAST_FOOD',
        '咖啡馆': 'CAFE',
        '酒吧': 'BAR',
        '街头美食': 'STREET_FOOD',
        '自助餐': 'BUFFET',
        '其他': 'OTHER',
    }
    
    # 价格范围映射
    PRICE_RANGE_MAP = {
        '经济型': '$',
        '中档': '$$',
        '高档': '$$$',
        '奢华': '$$$$',
        '$': '$',
        '$$': '$$',
        '$$$': '$$$',
        '$$$$': '$$$$',
    }
    
    # 酒店状态映射
    HOTEL_STATUS_MAP = {
        '营业中': 'ACTIVE',
        '未营业': 'INACTIVE',
        '装修中': 'RENOVATING',
        '已关闭': 'CLOSED',
        'ACTIVE': 'ACTIVE',
        'INACTIVE': 'INACTIVE',
        'RENOVATING': 'RENOVATING',
        'CLOSED': 'CLOSED',
    }
    
    # 酒店类型映射
    HOTEL_TYPE_MAP = {
        '奢华酒店': 'LUXURY',
        '商务酒店': 'BUSINESS',
        '度假酒店': 'RESORT',
        '精品酒店': 'BOUTIQUE',
        '青年旅舍': 'HOSTEL',
        '公寓酒店': 'APARTMENT',
        '民宿': 'HOMESTAY',
        '汽车旅馆': 'MOTEL',
        '其他': 'OTHER',
    }
    
    @classmethod
    def validate_attraction(cls, record: Dict[str, Any], index: int) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        验证景点数据
        
        Returns:
            (是否有效, 错误列表, 转换后的数据)
        """
        errors = []
        converted = {}
        
        # 必填字段验证
        if not record.get('attraction_name'):
            errors.append(f"记录 #{index}: 景点名称不能为空")
        else:
            converted['attraction_name'] = str(record['attraction_name']).strip()
        
        # 国家代码
        country_code = record.get('country_code')
        if pd.notna(country_code) and str(country_code).strip():
            converted['country_code'] = str(country_code).strip().upper()
        else:
            converted['country_code'] = 'CN'  # 默认值
        
        # 城市名称
        if record.get('city_name'):
            converted['city_name'] = str(record['city_name']).strip()
        else:
            errors.append(f"记录 #{index}: 城市名称不能为空")
        
        # 生成景点代码
        if converted.get('attraction_name'):
            base_code = converted['attraction_name'][:10].upper().replace(' ', '_')
            converted['attraction_code'] = f"ATT_{base_code}_{uuid.uuid4().hex[:8]}"
        
        # 地区
        if record.get('region'):
            converted['region'] = str(record['region']).strip()
        
        # 地址
        if record.get('address'):
            converted['address'] = str(record['address']).strip()
        
        # 分类映射
        if record.get('category'):
            category = str(record['category']).strip()
            converted['category'] = cls.ATTRACTION_CATEGORY_MAP.get(category, 'OTHER')
        
        # 子分类
        if record.get('subcategory'):
            converted['subcategory'] = str(record['subcategory']).strip()
        
        # 标签（转换为列表）
        if record.get('tags'):
            tags_str = str(record['tags']).strip()
            if tags_str and tags_str != '/':
                converted['tags'] = [tag.strip() for tag in tags_str.split() if tag.strip()]
            else:
                converted['tags'] = []
        else:
            converted['tags'] = []
        
        # 描述
        if record.get('description'):
            converted['description'] = str(record['description']).strip()
        
        # 特色（转换为列表）
        if record.get('highlights'):
            highlights_str = str(record['highlights']).strip()
            if highlights_str and highlights_str != '/':
                converted['highlights'] = [h.strip() for h in highlights_str.split('、') if h.strip()]
            else:
                converted['highlights'] = []
        else:
            converted['highlights'] = []
        
        # 建议游玩时长
        if record.get('recommended_duration'):
            try:
                duration = int(float(record['recommended_duration']))
                if duration > 0:
                    converted['recommended_duration'] = duration
            except (ValueError, TypeError):
                pass
        
        # 开放时间
        if record.get('opening_hours'):
            converted['opening_hours'] = str(record['opening_hours']).strip()
        
        # 最佳季节
        if record.get('best_season'):
            converted['best_season'] = str(record['best_season']).strip()
        
        # 是否24小时开放
        if record.get('is_always_open'):
            is_open = str(record['is_always_open']).strip()
            converted['is_always_open'] = is_open in ['是', 'True', 'true', '1', 'yes', 'YES']
        else:
            converted['is_always_open'] = False
        
        # 门票价格
        if record.get('ticket_price'):
            try:
                price = Decimal(str(record['ticket_price']))
                if price >= 0:
                    converted['ticket_price'] = price
            except (InvalidOperation, ValueError):
                pass
        
        # 货币
        converted['currency'] = 'CNY'
        
        # 票种
        if record.get('ticket_type'):
            converted['ticket_type'] = str(record['ticket_type']).strip()
        
        # 是否需要预订
        if record.get('booking_required'):
            booking = str(record['booking_required']).strip()
            converted['booking_required'] = booking in ['是', 'True', 'true', '1', 'yes', 'YES']
        else:
            converted['booking_required'] = False
        
        # 预订网站
        if record.get('booking_website'):
            converted['booking_website'] = str(record['booking_website']).strip()
        
        # 设施（转换为列表）
        if record.get('facilities'):
            facilities_str = str(record['facilities']).strip()
            if facilities_str and facilities_str != '/':
                converted['facilities'] = [f.strip() for f in facilities_str.split('、') if f.strip()]
            else:
                converted['facilities'] = []
        else:
            converted['facilities'] = []
        
        # 受欢迎度评分
        if record.get('popularity_score'):
            try:
                score = Decimal(str(record['popularity_score']))
                if 0 <= score <= 5:
                    converted['popularity_score'] = score
            except (InvalidOperation, ValueError):
                pass
        
        # 游客评分
        if record.get('visitor_rating'):
            try:
                score = Decimal(str(record['visitor_rating']))
                if 0 <= score <= 5:
                    converted['visitor_rating'] = score
            except (InvalidOperation, ValueError):
                pass
        
        # 评论数
        if record.get('review_count'):
            try:
                count = int(float(record['review_count']))
                if count >= 0:
                    converted['review_count'] = count
            except (ValueError, TypeError):
                pass
        
        # 主图URL
        if record.get('main_image_url'):
            converted['main_image_url'] = str(record['main_image_url']).strip()
        
        # 图片库
        if record.get('image_gallery'):
            gallery_str = str(record['image_gallery']).strip()
            if gallery_str and gallery_str != '/':
                converted['image_gallery'] = [url.strip() for url in gallery_str.split(',') if url.strip()]
            else:
                converted['image_gallery'] = []
        else:
            converted['image_gallery'] = []
        
        # 视频URL
        if record.get('video_url'):
            converted['video_url'] = str(record['video_url']).strip()
        
        # 状态
        if record.get('status'):
            status = str(record['status']).strip()
            converted['status'] = cls.ATTRACTION_STATUS_MAP.get(status, 'ACTIVE')
        else:
            converted['status'] = 'ACTIVE'
        
        # 创建人/更新人
        converted['created_by'] = 'system_import'
        converted['updated_by'] = 'system_import'
        
        # 版本
        converted['version'] = 1
        
        return len(errors) == 0, errors, converted
    
    @classmethod
    def validate_restaurant(cls, record: Dict[str, Any], index: int) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        验证餐厅数据
        
        Returns:
            (是否有效, 错误列表, 转换后的数据)
        """
        errors = []
        converted = {}
        
        # 必填字段验证
        if not record.get('restaurant_name'):
            errors.append(f"记录 #{index}: 餐厅名称不能为空")
        else:
            converted['restaurant_name'] = str(record['restaurant_name']).strip()
        
        # 国家代码
        country_code = record.get('country_code')
        if pd.notna(country_code) and str(country_code).strip():
            converted['country_code'] = str(country_code).strip().upper()
        else:
            converted['country_code'] = 'CN'  # 默认值
        
        # 城市名称
        if record.get('city_name'):
            converted['city_name'] = str(record['city_name']).strip()
        else:
            errors.append(f"记录 #{index}: 城市名称不能为空")
        
        # 生成餐厅代码
        if converted.get('restaurant_name'):
            base_code = converted['restaurant_name'][:10].upper().replace(' ', '_')
            converted['restaurant_code'] = f"RES_{base_code}_{uuid.uuid4().hex[:8]}"
        
        # 区域
        if record.get('district'):
            converted['district'] = str(record['district']).strip()
        
        # 地址
        if record.get('address'):
            converted['address'] = str(record['address']).strip()
        else:
            errors.append(f"记录 #{index}: 地址不能为空")
        
        # 菜系
        if record.get('cuisine_type'):
            converted['cuisine_type'] = str(record['cuisine_type']).strip()
        
        # 子菜系（转换为列表）
        if record.get('sub_cuisine_types'):
            sub_types_str = str(record['sub_cuisine_types']).strip()
            if sub_types_str and sub_types_str != '/':
                converted['sub_cuisine_types'] = [t.strip() for t in sub_types_str.split() if t.strip()]
            else:
                converted['sub_cuisine_types'] = []
        else:
            converted['sub_cuisine_types'] = []
        
        # 餐厅类型映射
        if record.get('restaurant_type'):
            rest_type = str(record['restaurant_type']).strip()
            converted['restaurant_type'] = cls.RESTAURANT_TYPE_MAP.get(rest_type, 'OTHER')
        
        # 标签（转换为字典）
        if record.get('tags'):
            tags_str = str(record['tags']).strip()
            if tags_str and tags_str != '/':
                tags_list = [tag.strip() for tag in tags_str.split() if tag.strip()]
                converted['tags'] = {tag: True for tag in tags_list}
            else:
                converted['tags'] = {}
        else:
            converted['tags'] = {}
        
        # 描述
        if record.get('description'):
            converted['description'] = str(record['description']).strip()
        
        # 招牌菜（转换为字典）
        if record.get('signature_dishes'):
            dishes_str = str(record['signature_dishes']).strip()
            if dishes_str and dishes_str != '/':
                dishes_list = [d.strip() for d in dishes_str.split('、') if d.strip()]
                converted['signature_dishes'] = {d: True for d in dishes_list}
            else:
                converted['signature_dishes'] = {}
        else:
            converted['signature_dishes'] = {}
        
        # 主厨名字
        if record.get('chef_name'):
            converted['chef_name'] = str(record['chef_name']).strip()
        
        # 建立年份
        if record.get('year_established'):
            try:
                year = int(float(record['year_established']))
                current_year = datetime.now().year
                if 1800 <= year <= current_year:
                    converted['year_established'] = year
            except (ValueError, TypeError):
                pass
        
        # 营业时间
        if record.get('opening_hours'):
            converted['opening_hours'] = str(record['opening_hours']).strip()
        
        # 是否24小时营业
        if record.get('is_24_hours'):
            is_24h = str(record['is_24_hours']).strip()
            converted['is_24_hours'] = is_24h in ['是', 'True', 'true', '1', 'yes', 'YES']
        else:
            converted['is_24_hours'] = False
        
        # 联系电话
        if record.get('contact_phone'):
            converted['contact_phone'] = str(record['contact_phone']).strip()
        
        # 联系邮箱
        if record.get('contact_email'):
            converted['contact_email'] = str(record['contact_email']).strip()
        
        # 网站
        if record.get('website'):
            converted['website'] = str(record['website']).strip()
        
        # 是否需要预订
        if record.get('reservation_required'):
            reservation = str(record['reservation_required']).strip()
            converted['reservation_required'] = reservation in ['是', 'True', 'true', '1', 'yes', 'YES']
        else:
            converted['reservation_required'] = False
        
        # 预订网站
        if record.get('reservation_website'):
            converted['reservation_website'] = str(record['reservation_website']).strip()
        
        # 价格范围
        if record.get('price_range'):
            price_range = str(record['price_range']).strip()
            converted['price_range'] = cls.PRICE_RANGE_MAP.get(price_range, '$$')
        
        # 人均价格
        if record.get('avg_price_per_person'):
            try:
                price = Decimal(str(record['avg_price_per_person']))
                if price >= 0:
                    converted['avg_price_per_person'] = price
            except (InvalidOperation, ValueError):
                pass
        
        # 设施（转换为字典）
        if record.get('amenities'):
            amenities_str = str(record['amenities']).strip()
            if amenities_str and amenities_str != '/':
                amenities_list = [a.strip() for a in amenities_str.split('、') if a.strip()]
                converted['amenities'] = {a: True for a in amenities_list}
            else:
                converted['amenities'] = {}
        else:
            converted['amenities'] = {}
        
        # 座位数
        if record.get('seating_capacity'):
            try:
                capacity = int(float(record['seating_capacity']))
                if capacity > 0:
                    converted['seating_capacity'] = capacity
            except (ValueError, TypeError):
                pass
        
        # 是否有包间
        if record.get('private_rooms_available'):
            has_rooms = str(record['private_rooms_available']).strip()
            converted['private_rooms_available'] = has_rooms in ['是', 'True', 'true', '1', 'yes', 'YES']
        else:
            converted['private_rooms_available'] = False
        
        # 饮食选项（转换为字典）
        if record.get('dietary_options'):
            options_str = str(record['dietary_options']).strip()
            if options_str and options_str != '/':
                options_list = [o.strip() for o in options_str.split('、') if o.strip()]
                converted['dietary_options'] = {o: True for o in options_list}
            else:
                converted['dietary_options'] = {}
        else:
            converted['dietary_options'] = {}
        
        # 是否提供酒精饮料
        if record.get('alcohol_served'):
            alcohol = str(record['alcohol_served']).strip()
            converted['alcohol_served'] = alcohol in ['是', 'True', 'true', '1', 'yes', 'YES']
        
        # 受欢迎度评分
        if record.get('popularity_score'):
            try:
                score = Decimal(str(record['popularity_score']))
                if 0 <= score <= 5:
                    converted['popularity_score'] = score
            except (InvalidOperation, ValueError):
                pass
        
        # 食物评分
        if record.get('food_rating'):
            try:
                score = Decimal(str(record['food_rating']))
                if 0 <= score <= 5:
                    converted['food_rating'] = score
            except (InvalidOperation, ValueError):
                pass
        
        # 服务评分
        if record.get('service_rating'):
            try:
                score = Decimal(str(record['service_rating']))
                if 0 <= score <= 5:
                    converted['service_rating'] = score
            except (InvalidOperation, ValueError):
                pass
        
        # 评论数
        if record.get('review_count'):
            try:
                count = int(float(record['review_count']))
                if count >= 0:
                    converted['review_count'] = count
            except (ValueError, TypeError):
                pass
        
        # 主图URL
        if record.get('main_image_url'):
            converted['main_image_url'] = str(record['main_image_url']).strip()
        
        # 状态
        if record.get('status'):
            status = str(record['status']).strip()
            converted['status'] = cls.RESTAURANT_STATUS_MAP.get(status, 'ACTIVE')
        else:
            converted['status'] = 'ACTIVE'
        
        # 创建人/更新人
        converted['created_by'] = 'system_import'
        converted['updated_by'] = 'system_import'
        
        # 版本
        converted['version'] = 1
        
        return len(errors) == 0, errors, converted
    
    @classmethod
    def validate_hotel(cls, record: Dict[str, Any], index: int) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        验证酒店数据
        
        Returns:
            (是否有效, 错误列表, 转换后的数据)
        """
        errors = []
        converted = {}
        
        # 必填字段验证
        if not record.get('hotel_name'):
            errors.append(f"记录 #{index}: 酒店名称不能为空")
        else:
            converted['hotel_name'] = str(record['hotel_name']).strip()
        
        # 国家代码
        country_code = record.get('country_code')
        if pd.notna(country_code) and str(country_code).strip():
            converted['country_code'] = str(country_code).strip().upper()
        else:
            converted['country_code'] = 'CN'  # 默认值
        
        # 城市名称
        if record.get('city_name'):
            converted['city_name'] = str(record['city_name']).strip()
        else:
            errors.append(f"记录 #{index}: 城市名称不能为空")
        
        # 生成酒店代码
        if converted.get('hotel_name'):
            base_code = converted['hotel_name'][:10].upper().replace(' ', '_')
            converted['hotel_code'] = f"HOT_{base_code}_{uuid.uuid4().hex[:8]}"
        
        # 品牌名称
        if record.get('brand_name'):
            converted['brand_name'] = str(record['brand_name']).strip()
        
        # 区域
        if record.get('district'):
            converted['district'] = str(record['district']).strip()
        
        # 地址
        if record.get('address'):
            converted['address'] = str(record['address']).strip()
        else:
            errors.append(f"记录 #{index}: 地址不能为空")
        
        # 纬度
        if record.get('latitude'):
            try:
                latitude = Decimal(str(record['latitude']))
                if -90 <= latitude <= 90:
                    converted['latitude'] = latitude
            except (InvalidOperation, ValueError):
                pass
        
        # 经度
        if record.get('longitude'):
            try:
                longitude = Decimal(str(record['longitude']))
                if -180 <= longitude <= 180:
                    converted['longitude'] = longitude
            except (InvalidOperation, ValueError):
                pass
        
        # 星级
        if record.get('hotel_star'):
            try:
                star = int(float(record['hotel_star']))
                if 1 <= star <= 5:
                    converted['hotel_star'] = star
            except (ValueError, TypeError):
                pass
        
        # 酒店类型映射
        if record.get('hotel_type'):
            hotel_type = str(record['hotel_type']).strip()
            converted['hotel_type'] = cls.HOTEL_TYPE_MAP.get(hotel_type, 'OTHER')
        
        # 标签（转换为字典）
        if record.get('tags'):
            tags_str = str(record['tags']).strip()
            if tags_str and tags_str != '/':
                tags_list = [tag.strip() for tag in tags_str.split() if tag.strip()]
                converted['tags'] = {tag: True for tag in tags_list}
            else:
                converted['tags'] = {}
        else:
            converted['tags'] = {}
        
        # 描述
        if record.get('description'):
            converted['description'] = str(record['description']).strip()
        
        # 入住时间
        if record.get('check_in_time'):
            try:
                check_in = str(record['check_in_time']).strip()
                if check_in:
                    converted['check_in_time'] = check_in
            except:
                pass
        else:
            converted['check_in_time'] = '14:00'
        
        # 退房时间
        if record.get('check_out_time'):
            try:
                check_out = str(record['check_out_time']).strip()
                if check_out:
                    converted['check_out_time'] = check_out
            except:
                pass
        else:
            converted['check_out_time'] = '12:00'
        
        # 联系电话
        if record.get('contact_phone'):
            converted['contact_phone'] = str(record['contact_phone']).strip()
        
        # 联系邮箱
        if record.get('contact_email'):
            converted['contact_email'] = str(record['contact_email']).strip()
        
        # 网站
        if record.get('website'):
            converted['website'] = str(record['website']).strip()
        
        # 设施（转换为字典）
        if record.get('amenities'):
            amenities_str = str(record['amenities']).strip()
            if amenities_str and amenities_str != '/':
                amenities_list = [a.strip() for a in amenities_str.split('、') if a.strip()]
                converted['amenities'] = {a: True for a in amenities_list}
            else:
                converted['amenities'] = {}
        else:
            converted['amenities'] = {}
        
        # 房间设施（转换为字典）
        if record.get('room_facilities'):
            room_facilities_str = str(record['room_facilities']).strip()
            if room_facilities_str and room_facilities_str != '/':
                room_facilities_list = [r.strip() for r in room_facilities_str.split('、') if r.strip()]
                converted['room_facilities'] = {r: True for r in room_facilities_list}
            else:
                converted['room_facilities'] = {}
        else:
            converted['room_facilities'] = {}
        
        # 商务设施（转换为字典）
        if record.get('business_facilities'):
            business_facilities_str = str(record['business_facilities']).strip()
            if business_facilities_str and business_facilities_str != '/':
                business_facilities_list = [b.strip() for b in business_facilities_str.split('、') if b.strip()]
                converted['business_facilities'] = {b: True for b in business_facilities_list}
            else:
                converted['business_facilities'] = {}
        else:
            converted['business_facilities'] = {}
        
        # 房型信息（转换为字典）
        if record.get('room_types'):
            room_types_str = str(record['room_types']).strip()
            if room_types_str and room_types_str != '/':
                room_types_list = [r.strip() for r in room_types_str.split('、') if r.strip()]
                converted['room_types'] = {r: True for r in room_types_list}
            else:
                converted['room_types'] = {}
        else:
            converted['room_types'] = {}
        
        # 价格范围
        if record.get('price_range'):
            converted['price_range'] = str(record['price_range']).strip()
        
        # 货币
        converted['currency'] = 'CNY'
        
        # 最低价格
        if record.get('min_price'):
            try:
                price = Decimal(str(record['min_price']))
                if price >= 0:
                    converted['min_price'] = price
            except (InvalidOperation, ValueError):
                pass
        
        # 最高价格
        if record.get('max_price'):
            try:
                price = Decimal(str(record['max_price']))
                if price >= 0:
                    converted['max_price'] = price
            except (InvalidOperation, ValueError):
                pass
        
        # 受欢迎度评分
        if record.get('popularity_score'):
            try:
                score = Decimal(str(record['popularity_score']))
                if 0 <= score <= 5:
                    converted['popularity_score'] = score
            except (InvalidOperation, ValueError):
                pass
        
        # 客人评分
        if record.get('guest_rating'):
            try:
                score = Decimal(str(record['guest_rating']))
                if 0 <= score <= 5:
                    converted['guest_rating'] = score
            except (InvalidOperation, ValueError):
                pass
        
        # 评论数
        if record.get('review_count'):
            try:
                count = int(float(record['review_count']))
                if count >= 0:
                    converted['review_count'] = count
            except (ValueError, TypeError):
                pass
        
        # 主图URL
        if record.get('main_image_url'):
            converted['main_image_url'] = str(record['main_image_url']).strip()
        
        # 图片库（转换为列表）
        if record.get('image_gallery'):
            gallery_str = str(record['image_gallery']).strip()
            if gallery_str and gallery_str != '/':
                converted['image_gallery'] = [url.strip() for url in gallery_str.split(',') if url.strip()]
            else:
                converted['image_gallery'] = []
        else:
            converted['image_gallery'] = []
        
        # 状态
        if record.get('status'):
            status = str(record['status']).strip()
            converted['status'] = cls.HOTEL_STATUS_MAP.get(status, 'ACTIVE')
        else:
            converted['status'] = 'ACTIVE'
        
        # 创建人/更新人
        converted['created_by'] = 'system_import'
        converted['updated_by'] = 'system_import'
        
        # 版本
        converted['version'] = 1
        
        return len(errors) == 0, errors, converted


class DataImporter:
    """数据导入器"""
    
    @staticmethod
    def import_attractions(records: List[Dict[str, Any]], report: ImportReport) -> ImportReport:
        """导入景点数据"""
        logger.info(f"开始导入 {len(records)} 条景点记录")
        report.records_total = len(records)
        
        for index, record in enumerate(records):
            try:
                # 验证数据
                is_valid, errors, converted = DataValidator.validate_attraction(record, index)
                
                if not is_valid:
                    for error in errors:
                        report.add_error(index, 'validation', record, error)
                    continue
                
                # 检查是否已存在（根据名称和城市）
                existing = Attraction.objects.filter(
                    attraction_name=converted['attraction_name'],
                    city_name=converted['city_name']
                ).first()
                
                if existing:
                    # 更新现有记录
                    for key, value in converted.items():
                        setattr(existing, key, value)
                    existing.save()
                    logger.debug(f"更新景点: {converted['attraction_name']}")
                else:
                    # 创建新记录
                    Attraction.objects.create(**converted)
                    logger.debug(f"创建景点: {converted['attraction_name']}")
                
                report.add_success()
                
            except Exception as e:
                logger.error(f"导入景点记录 #{index} 失败: {e}")
                report.add_error(index, 'import', record, str(e))
        
        return report
    
    @staticmethod
    def import_restaurants(records: List[Dict[str, Any]], report: ImportReport) -> ImportReport:
        """导入餐厅数据"""
        logger.info(f"开始导入 {len(records)} 条餐厅记录")
        report.records_total = len(records)
        
        for index, record in enumerate(records):
            try:
                # 验证数据
                is_valid, errors, converted = DataValidator.validate_restaurant(record, index)
                
                if not is_valid:
                    for error in errors:
                        report.add_error(index, 'validation', record, error)
                    continue
                
                # 检查是否已存在（根据名称和地址）
                existing = Restaurant.objects.filter(
                    restaurant_name=converted['restaurant_name'],
                    address=converted.get('address', '')
                ).first()
                
                if existing:
                    # 更新现有记录
                    for key, value in converted.items():
                        setattr(existing, key, value)
                    existing.save()
                    logger.debug(f"更新餐厅: {converted['restaurant_name']}")
                else:
                    # 创建新记录
                    Restaurant.objects.create(**converted)
                    logger.debug(f"创建餐厅: {converted['restaurant_name']}")
                
                report.add_success()
                
            except Exception as e:
                logger.error(f"导入餐厅记录 #{index} 失败: {e}")
                report.add_error(index, 'import', record, str(e))
        
        return report
    
    @staticmethod
    def import_hotels(records: List[Dict[str, Any]], report: ImportReport) -> ImportReport:
        """导入酒店数据"""
        logger.info(f"开始导入 {len(records)} 条酒店记录")
        report.records_total = len(records)
        
        for index, record in enumerate(records):
            try:
                # 验证数据
                is_valid, errors, converted = DataValidator.validate_hotel(record, index)
                
                if not is_valid:
                    for error in errors:
                        report.add_error(index, 'validation', record, error)
                    continue
                
                # 检查是否已存在（根据名称和地址）
                existing = Hotel.objects.filter(
                    hotel_name=converted['hotel_name'],
                    address=converted.get('address', '')
                ).first()
                
                if existing:
                    # 更新现有记录
                    for key, value in converted.items():
                        setattr(existing, key, value)
                    existing.save()
                    logger.debug(f"更新酒店: {converted['hotel_name']}")
                else:
                    # 创建新记录
                    Hotel.objects.create(**converted)
                    logger.debug(f"创建酒店: {converted['hotel_name']}")
                
                report.add_success()
                
            except Exception as e:
                logger.error(f"导入酒店记录 #{index} 失败: {e}")
                report.add_error(index, 'import', record, str(e))
        
        return report


class Command(BaseCommand):
    """Django管理命令：导入Excel数据"""
    
    help = '将Excel文件数据导入到数据库表中'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--attractions',
            type=str,
            help='景点数据Excel文件路径'
        )
        parser.add_argument(
            '--restaurants',
            type=str,
            help='餐厅数据Excel文件路径'
        )
        parser.add_argument(
            '--hotels',
            type=str,
            help='酒店数据Excel文件路径'
        )
        parser.add_argument(
            '--output',
            type=str,
            default='import_report.json',
            help='导入报告输出文件路径（JSON格式）'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='试运行模式，不实际写入数据库'
        )
    
    def handle(self, *args, **options):
        attractions_file = options.get('attractions')
        restaurants_file = options.get('restaurants')
        hotels_file = options.get('hotels')
        output_file = options['output']
        dry_run = options['dry_run']
        
        if not attractions_file and not restaurants_file and not hotels_file:
            raise CommandError('请至少指定 --attractions 或 --restaurants 或 --hotels 参数')
        
        reports = {}
        
        # 导入景点数据
        if attractions_file:
            self.stdout.write(self.style.NOTICE(f'开始导入景点数据: {attractions_file}'))
            report = ImportReport()
            
            try:
                records = ExcelDataReader.read_excel(attractions_file)
                if not dry_run:
                    DataImporter.import_attractions(records, report)
                else:
                    # 试运行模式：只验证数据
                    report.records_total = len(records)
                    for index, record in enumerate(records):
                        is_valid, errors, converted = DataValidator.validate_attraction(record, index)
                        if is_valid:
                            report.add_success()
                        else:
                            for error in errors:
                                report.add_error(index, 'validation', record, error)
                    self.stdout.write(self.style.WARNING('试运行模式：数据已验证但未写入数据库'))
                
                report.finalize()
                reports['attractions'] = report.to_dict()
                self.stdout.write(self.style.SUCCESS(f'景点数据导入完成: {report.records_success}/{report.records_total}'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'景点数据导入失败: {e}'))
                raise
        
        # 导入餐厅数据
        if restaurants_file:
            self.stdout.write(self.style.NOTICE(f'开始导入餐厅数据: {restaurants_file}'))
            report = ImportReport()
            
            try:
                records = ExcelDataReader.read_excel(restaurants_file)
                if not dry_run:
                    DataImporter.import_restaurants(records, report)
                else:
                    # 试运行模式：只验证数据
                    report.records_total = len(records)
                    for index, record in enumerate(records):
                        is_valid, errors, converted = DataValidator.validate_restaurant(record, index)
                        if is_valid:
                            report.add_success()
                        else:
                            for error in errors:
                                report.add_error(index, 'validation', record, error)
                    self.stdout.write(self.style.WARNING('试运行模式：数据已验证但未写入数据库'))
                
                report.finalize()
                reports['restaurants'] = report.to_dict()
                self.stdout.write(self.style.SUCCESS(f'餐厅数据导入完成: {report.records_success}/{report.records_total}'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'餐厅数据导入失败: {e}'))
                raise
        
        # 导入酒店数据
        if hotels_file:
            self.stdout.write(self.style.NOTICE(f'开始导入酒店数据: {hotels_file}'))
            report = ImportReport()
            
            try:
                records = ExcelDataReader.read_excel(hotels_file)
                if not dry_run:
                    DataImporter.import_hotels(records, report)
                else:
                    # 试运行模式：只验证数据
                    report.records_total = len(records)
                    for index, record in enumerate(records):
                        is_valid, errors, converted = DataValidator.validate_hotel(record, index)
                        if is_valid:
                            report.add_success()
                        else:
                            for error in errors:
                                report.add_error(index, 'validation', record, error)
                    self.stdout.write(self.style.WARNING('试运行模式：数据已验证但未写入数据库'))
                
                report.finalize()
                reports['hotels'] = report.to_dict()
                self.stdout.write(self.style.SUCCESS(f'酒店数据导入完成: {report.records_success}/{report.records_total}'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'酒店数据导入失败: {e}'))
                raise
        
        # 保存导入报告
        if reports:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(reports, f, ensure_ascii=False, indent=2)
            self.stdout.write(self.style.SUCCESS(f'导入报告已保存: {output_file}'))
            
            # 打印文本报告
            for data_type, report_data in reports.items():
                self.stdout.write(f"\n{'='*60}")
                self.stdout.write(f"{data_type.upper()} 导入报告:")
                self.stdout.write(f"{'='*60}")
                self.stdout.write(f"总记录数: {report_data['records_total']}")
                self.stdout.write(f"成功导入: {report_data['records_success']}")
                self.stdout.write(f"失败记录: {report_data['records_failed']}")
                self.stdout.write(f"成功率: {report_data['success_rate']}")
                if report_data['errors']:
                    self.stdout.write(self.style.ERROR(f"错误数: {len(report_data['errors'])}"))
