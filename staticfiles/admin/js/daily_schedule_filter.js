(function($) {
    console.log('Daily Schedule Filter JS file loaded');
    
    $(document).ready(function() {
        console.log('Document ready event fired');
        
        // 直接获取表单字段，不再使用setTimeout
        console.log('Searching for form fields...');
        
        // 获取表单字段
        var destinationField = $('select[name="destination_id"]');
        var attractionField = $('select[name="attraction_id"]');
        var restaurantField = $('select[name="restaurant_id"]');
        var hotelField = $('select[name="hotel_id"]');
        
        console.log('Form fields found:');
        console.log('destinationField:', destinationField.length > 0 ? 'Yes' : 'No');
        console.log('attractionField:', attractionField.length > 0 ? 'Yes' : 'No');
        console.log('restaurantField:', restaurantField.length > 0 ? 'Yes' : 'No');
        console.log('hotelField:', hotelField.length > 0 ? 'Yes' : 'No');
        
        // 检查是否找到destination字段
        if (destinationField.length === 0) {
            console.error('Destination field not found!');
            console.log('All select elements on page:', $('select').length);
            $('select').each(function(index, element) {
                console.log('Select element ' + index + ':', $(element).attr('name'));
            });
            return;
        }
        
        // 保存原始的选项，以便在需要时恢复
        var originalAttractionOptions = attractionField.html();
        var originalRestaurantOptions = restaurantField.html();
        var originalHotelOptions = hotelField.html();
        
        console.log('Original options saved');
        
        // 创建加载状态指示器
        var loadingIndicator = $('<span>', {
            'class': 'loading-indicator',
            'style': 'margin-left: 10px; color: #666; font-size: 12px;',
            'text': '加载中...'
        }).hide();
        destinationField.after(loadingIndicator);
        
        // 监听destination字段变化
        console.log('Binding change event to destination field...');
        destinationField.change(function() {
            console.log('Destination field changed');
            var destinationId = $(this).val();
            console.log('Selected destination ID:', destinationId);
            
            // 保存当前选中的值
            var currentAttractionValue = attractionField.val();
            var currentRestaurantValue = restaurantField.val();
            var currentHotelValue = hotelField.val();
            console.log('Current selected values:', {
                attraction: currentAttractionValue,
                restaurant: currentRestaurantValue,
                hotel: currentHotelValue
            });
            
            // 显示加载状态
            loadingIndicator.show();
            
            // 清空现有的选项
            console.log('Clearing existing options...');
            attractionField.empty().append('<option value="">---------</option>');
            restaurantField.empty().append('<option value="">---------</option>');
            hotelField.empty().append('<option value="">---------</option>');
            
            if (destinationId) {
                console.log('Sending AJAX request for filtered resources');
                // 发送AJAX请求获取过滤后的资源
                $.ajax({
                    url: '/admin/get_filtered_resources/',
                    type: 'GET',
                    data: { 'destination_id': destinationId },
                    dataType: 'json',
                    success: function(data) {
                        console.log('AJAX response received:', data);
                        
                        // 隐藏加载状态
                        loadingIndicator.hide();
                        
                        // 更新景点选项
                        if (data.attractions.length > 0) {
                            console.log('Updating attractions with ' + data.attractions.length + ' options');
                            var attractionFound = false;
                            $.each(data.attractions, function(index, attraction) {
                                var option = $('<option>', {
                                    value: attraction.attraction_id,
                                    text: attraction.attraction_name
                                });
                                // 恢复选中状态
                                if (attraction.attraction_id === currentAttractionValue) {
                                    option.prop('selected', true);
                                    attractionFound = true;
                                }
                                attractionField.append(option);
                            });
                            // 如果之前选中的景点不在新结果中，清空选中状态
                            if (!attractionFound && currentAttractionValue) {
                                console.log('Previously selected attraction not found in new results');
                            }
                        } else {
                            console.log('No attractions found for this destination');
                        }
                        
                        // 更新餐厅选项
                        if (data.restaurants.length > 0) {
                            console.log('Updating restaurants with ' + data.restaurants.length + ' options');
                            var restaurantFound = false;
                            $.each(data.restaurants, function(index, restaurant) {
                                var option = $('<option>', {
                                    value: restaurant.restaurant_id,
                                    text: restaurant.restaurant_name
                                });
                                // 恢复选中状态
                                if (restaurant.restaurant_id === currentRestaurantValue) {
                                    option.prop('selected', true);
                                    restaurantFound = true;
                                }
                                restaurantField.append(option);
                            });
                            // 如果之前选中的餐厅不在新结果中，清空选中状态
                            if (!restaurantFound && currentRestaurantValue) {
                                console.log('Previously selected restaurant not found in new results');
                            }
                        } else {
                            console.log('No restaurants found for this destination');
                        }
                        
                        // 更新酒店选项
                        if (data.hotels.length > 0) {
                            console.log('Updating hotels with ' + data.hotels.length + ' options');
                            var hotelFound = false;
                            $.each(data.hotels, function(index, hotel) {
                                var option = $('<option>', {
                                    value: hotel.hotel_id,
                                    text: hotel.hotel_name
                                });
                                // 恢复选中状态
                                if (hotel.hotel_id === currentHotelValue) {
                                    option.prop('selected', true);
                                    hotelFound = true;
                                }
                                hotelField.append(option);
                            });
                            // 如果之前选中的酒店不在新结果中，清空选中状态
                            if (!hotelFound && currentHotelValue) {
                                console.log('Previously selected hotel not found in new results');
                            }
                        } else {
                            console.log('No hotels found for this destination');
                        }
                    },
                    error: function(xhr, status, error) {
                        console.error('AJAX error:', status, error);
                        console.error('Response:', xhr.responseText);
                        
                        // 隐藏加载状态
                        loadingIndicator.hide();
                        
                        // 显示错误信息
                        var errorMessage = $('<div>', {
                            'class': 'error-message',
                            'style': 'margin-top: 10px; padding: 10px; background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; border-radius: 4px; font-size: 14px;',
                            'text': '加载资源失败，请重试'
                        });
                        destinationField.after(errorMessage);
                        setTimeout(function() {
                            errorMessage.fadeOut('slow', function() {
                                $(this).remove();
                            });
                        }, 3000);
                        
                        // 恢复原始选项
                        console.log('Restoring original options due to AJAX error');
                        attractionField.html(originalAttractionOptions);
                        restaurantField.html(originalRestaurantOptions);
                        hotelField.html(originalHotelOptions);
                        // 恢复选中状态
                        if (currentAttractionValue) {
                            attractionField.val(currentAttractionValue);
                        }
                        if (currentRestaurantValue) {
                            restaurantField.val(currentRestaurantValue);
                        }
                        if (currentHotelValue) {
                            hotelField.val(currentHotelValue);
                        }
                    }
                });
            } else {
                console.log('No destination selected, restoring original options');
                
                // 隐藏加载状态
                loadingIndicator.hide();
                
                // 如果没有选择destination，恢复原始选项
                attractionField.html(originalAttractionOptions);
                restaurantField.html(originalRestaurantOptions);
                hotelField.html(originalHotelOptions);
                // 恢复选中状态
                if (currentAttractionValue) {
                    attractionField.val(currentAttractionValue);
                }
                if (currentRestaurantValue) {
                    restaurantField.val(currentRestaurantValue);
                }
                if (currentHotelValue) {
                    hotelField.val(currentHotelValue);
                }
            }
        });
        
        console.log('Change event bound successfully');
        
        // 页面加载时，如果已经有选择的destination，触发一次change事件
        console.log('Initial destination value:', destinationField.val());
        if (destinationField.val()) {
            console.log('Triggering initial change event');
            destinationField.trigger('change');
        }
    });
})(django.jQuery);
