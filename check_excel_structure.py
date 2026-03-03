#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查Excel文件结构 - 转置数据结构
"""
import pandas as pd
import sys

def check_excel_structure(file_path, name):
    """检查Excel文件结构"""
    print(f"\n{'='*60}")
    print(f"检查文件: {name}")
    print(f"路径: {file_path}")
    print(f"{'='*60}")
    
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path, header=None)
        
        print(f"\n原始数据结构:")
        print(f"总行数: {len(df)}")
        print(f"总列数: {len(df.columns)}")
        
        # 转置数据 - 字段名在第一列，数据在后续列
        # 跳过前4行（元数据行）
        data_df = df.iloc[4:].copy()
        
        # 第一列是字段名
        field_names = data_df.iloc[:, 0].tolist()
        print(f"\n字段列表 ({len(field_names)}个):")
        for i, field in enumerate(field_names, 1):
            print(f"  {i}. {field}")
        
        # 转置：字段名作为列名，每列是一条记录
        # 从第4列开始是数据（第0列是字段名，第1列是类型，第2列是描述，第3列可能是空列）
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
        
        print(f"\n解析到的记录数: {len(records)}")
        
        if records:
            print(f"\n第一条记录示例:")
            for k, v in list(records[0].items())[:15]:
                print(f"  {k}: {v}")
        
        return records
    except Exception as e:
        print(f"读取文件出错: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 检查命令行参数指定的文件
        for i, file_path in enumerate(sys.argv[1:], 1):
            check_excel_structure(file_path, f"文件 {i}")
    else:
        # 默认检查景点和餐厅文件
        # 检查景点文件
        attraction_file = r"c:\project\smart_trip_quote\tests\景点集合信息.xlsx"
        attraction_records = check_excel_structure(attraction_file, "景点集合信息")
        
        # 检查餐厅文件
        restaurant_file = r"c:\project\smart_trip_quote\tests\餐厅集合信息.xlsx"
        restaurant_records = check_excel_structure(restaurant_file, "餐厅集合信息")
