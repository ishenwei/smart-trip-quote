from django.core.cache import cache
import json
import os


class CountryCodeDict:
    """ISO 3166-1 alpha-2 国家代码数据字典"""
    
    # 缓存键
    CACHE_KEY = 'country_code_dict'
    CACHE_TIMEOUT = 86400  # 24小时
    
    # 国家代码数据
    COUNTRY_CODES = {
        'AF': '阿富汗',
        'AL': '阿尔巴尼亚',
        'DZ': '阿尔及利亚',
        'AD': '安道尔',
        'AO': '安哥拉',
        'AG': '安提瓜和巴布达',
        'AR': '阿根廷',
        'AM': '亚美尼亚',
        'AU': '澳大利亚',
        'AT': '奥地利',
        'AZ': '阿塞拜疆',
        'BS': '巴哈马',
        'BH': '巴林',
        'BD': '孟加拉国',
        'BB': '巴巴多斯',
        'BY': '白俄罗斯',
        'BE': '比利时',
        'BZ': '伯利兹',
        'BJ': '贝宁',
        'BT': '不丹',
        'BO': '玻利维亚',
        'BA': '波斯尼亚和黑塞哥维那',
        'BW': '博茨瓦纳',
        'BR': '巴西',
        'BN': '文莱',
        'BG': '保加利亚',
        'BF': '布基纳法索',
        'BI': '布隆迪',
        'CV': '佛得角',
        'KH': '柬埔寨',
        'CM': '喀麦隆',
        'CA': '加拿大',
        'CF': '中非共和国',
        'TD': '乍得',
        'CL': '智利',
        'CN': '中国',
        'CO': '哥伦比亚',
        'KM': '科摩罗',
        'CG': '刚果（布）',
        'CD': '刚果（金）',
        'CR': '哥斯达黎加',
        'CI': '科特迪瓦',
        'HR': '克罗地亚',
        'CU': '古巴',
        'CY': '塞浦路斯',
        'CZ': '捷克',
        'DK': '丹麦',
        'DJ': '吉布提',
        'DO': '多米尼加共和国',
        'EC': '厄瓜多尔',
        'EG': '埃及',
        'SV': '萨尔瓦多',
        'GQ': '赤道几内亚',
        'ER': '厄立特里亚',
        'EE': '爱沙尼亚',
        'ET': '埃塞俄比亚',
        'FJ': '斐济',
        'FI': '芬兰',
        'FR': '法国',
        'GA': '加蓬',
        'GM': '冈比亚',
        'GE': '格鲁吉亚',
        'DE': '德国',
        'GH': '加纳',
        'GR': '希腊',
        'GT': '危地马拉',
        'GN': '几内亚',
        'GW': '几内亚比绍',
        'GY': '圭亚那',
        'HT': '海地',
        'HN': '洪都拉斯',
        'HK': '中国香港',
        'HU': '匈牙利',
        'IS': '冰岛',
        'IN': '印度',
        'ID': '印度尼西亚',
        'IR': '伊朗',
        'IQ': '伊拉克',
        'IE': '爱尔兰',
        'IL': '以色列',
        'IT': '意大利',
        'JM': '牙买加',
        'JP': '日本',
        'JO': '约旦',
        'KZ': '哈萨克斯坦',
        'KE': '肯尼亚',
        'KR': '韩国',
        'KW': '科威特',
        'KG': '吉尔吉斯斯坦',
        'LA': '老挝',
        'LV': '拉脱维亚',
        'LB': '黎巴嫩',
        'LS': '莱索托',
        'LR': '利比里亚',
        'LY': '利比亚',
        'LT': '立陶宛',
        'LU': '卢森堡',
        'MO': '中国澳门',
        'MG': '马达加斯加',
        'MW': '马拉维',
        'MY': '马来西亚',
        'ML': '马里',
        'MR': '毛里塔尼亚',
        'MU': '毛里求斯',
        'MX': '墨西哥',
        'MD': '摩尔多瓦',
        'MN': '蒙古',
        'ME': '黑山',
        'MA': '摩洛哥',
        'MZ': '莫桑比克',
        'MM': '缅甸',
        'NA': '纳米比亚',
        'NP': '尼泊尔',
        'NL': '荷兰',
        'NZ': '新西兰',
        'NI': '尼加拉瓜',
        'NE': '尼日尔',
        'NG': '尼日利亚',
        'MK': '北马其顿',
        'NO': '挪威',
        'OM': '阿曼',
        'PK': '巴基斯坦',
        'PA': '巴拿马',
        'PG': '巴布亚新几内亚',
        'PY': '巴拉圭',
        'PE': '秘鲁',
        'PH': '菲律宾',
        'PL': '波兰',
        'PT': '葡萄牙',
        'PR': '波多黎各',
        'QA': '卡塔尔',
        'RO': '罗马尼亚',
        'RU': '俄罗斯',
        'RW': '卢旺达',
        'SA': '沙特阿拉伯',
        'SN': '塞内加尔',
        'RS': '塞尔维亚',
        'SC': '塞舌尔',
        'SL': '塞拉利昂',
        'SG': '新加坡',
        'SK': '斯洛伐克',
        'SI': '斯洛文尼亚',
        'SB': '所罗门群岛',
        'SO': '索马里',
        'ZA': '南非',
        'ES': '西班牙',
        'LK': '斯里兰卡',
        'SD': '苏丹',
        'SR': '苏里南',
        'SE': '瑞典',
        'CH': '瑞士',
        'SY': '叙利亚',
        'TW': '中国台湾',
        'TJ': '塔吉克斯坦',
        'TZ': '坦桑尼亚',
        'TH': '泰国',
        'TG': '多哥',
        'TT': '特立尼达和多巴哥',
        'TN': '突尼斯',
        'TR': '土耳其',
        'TM': '土库曼斯坦',
        'UG': '乌干达',
        'UA': '乌克兰',
        'AE': '阿拉伯联合酋长国',
        'GB': '英国',
        'US': '美国',
        'UY': '乌拉圭',
        'UZ': '乌兹别克斯坦',
        'VE': '委内瑞拉',
        'VN': '越南',
        'YE': '也门',
        'ZM': '赞比亚',
        'ZW': '津巴布韦'
    }
    
    @classmethod
    def get_country_name(cls, country_code):
        """
        根据国家代码获取中文名称
        
        Args:
            country_code: ISO 3166-1 alpha-2 格式的国家代码
            
        Returns:
            str: 国家中文名称，如果未找到则返回空字符串
        """
        # 尝试从缓存获取
        country_dict = cls._get_from_cache()
        
        # 如果缓存中没有，使用内置数据
        if country_dict is None:
            country_dict = cls.COUNTRY_CODES
            # 更新缓存
            cls._update_cache(country_dict)
        
        return country_dict.get(country_code.upper(), '')
    
    @classmethod
    def get_all_countries(cls):
        """
        获取所有国家代码和名称的字典
        
        Returns:
            dict: 国家代码到中文名称的映射
        """
        # 尝试从缓存获取
        country_dict = cls._get_from_cache()
        
        # 如果缓存中没有，使用内置数据
        if country_dict is None:
            country_dict = cls.COUNTRY_CODES
            # 更新缓存
            cls._update_cache(country_dict)
        
        return country_dict
    
    @classmethod
    def _get_from_cache(cls):
        """
        从缓存获取国家代码字典
        
        Returns:
            dict or None: 国家代码字典或None
        """
        try:
            cached_data = cache.get(cls.CACHE_KEY)
            if cached_data:
                return cached_data
        except Exception:
            # 缓存读取失败，返回None
            pass
        return None
    
    @classmethod
    def _update_cache(cls, country_dict):
        """
        更新缓存中的国家代码字典
        
        Args:
            country_dict: 国家代码字典
        """
        try:
            cache.set(cls.CACHE_KEY, country_dict, cls.CACHE_TIMEOUT)
        except Exception:
            # 缓存更新失败，忽略错误
            pass
    
    @classmethod
    def refresh_cache(cls):
        """
        刷新缓存，重新加载国家代码数据
        """
        cls._update_cache(cls.COUNTRY_CODES)
    
    @classmethod
    def update_country_codes(cls, new_codes):
        """
        更新国家代码数据
        
        Args:
            new_codes: 新的国家代码字典
        """
        # 更新内置数据
        cls.COUNTRY_CODES.update(new_codes)
        # 刷新缓存
        cls.refresh_cache()
    
    @classmethod
    def load_from_file(cls, file_path):
        """
        从文件加载国家代码数据
        
        Args:
            file_path: JSON文件路径
        """
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    new_codes = json.load(f)
                    cls.update_country_codes(new_codes)
                return True
        except Exception:
            # 文件加载失败，忽略错误
            pass
        return False
