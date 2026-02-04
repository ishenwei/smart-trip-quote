(function($) {
    console.log('Daily Schedule Filter JS file loaded');
    
    $(document).ready(function() {
        console.log('Document ready event fired');
        
        // 等待DOM完全加载后再获取元素
        setTimeout(function() {
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
            
            // 监听destination字段变化
            console.log('Binding change event to destination field...');
            destinationField.change(function() {
                console.log('Destination field changed');
                var destinationId = $(this).val();
                console.log('Selected destination ID:', destinationId);
                
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
                            // 更新景点选项
                            if (data.attractions.length > 0) {
                                console.log('Updating attractions with ' + data.attractions.length + ' options');
                                $.each(data.attractions, function(index, attraction) {
                                    attractionField.append($('<option>', {
                                        value: attraction.attraction_id,
                                        text: attraction.attraction_name
                                    }));
                                });
                            } else {
                                console.log('No attractions found for this destination');
                            }
                            
                            // 更新餐厅选项
                            if (data.restaurants.length > 0) {
                                console.log('Updating restaurants with ' + data.restaurants.length + ' options');
                                $.each(data.restaurants, function(index, restaurant) {
                                    restaurantField.append($('<option>', {
                                        value: restaurant.restaurant_id,
                                        text: restaurant.restaurant_name
                                    }));
                                });
                            } else {
                                console.log('No restaurants found for this destination');
                            }
                            
                            // 更新酒店选项
                            if (data.hotels.length > 0) {
                                console.log('Updating hotels with ' + data.hotels.length + ' options');
                                $.each(data.hotels, function(index, hotel) {
                                    hotelField.append($('<option>', {
                                        value: hotel.hotel_id,
                                        text: hotel.hotel_name
                                    }));
                                });
                            } else {
                                console.log('No hotels found for this destination');
                            }
                        },
                        error: function(xhr, status, error) {
                            console.error('AJAX error:', status, error);
                            console.error('Response:', xhr.responseText);
                            // 恢复原始选项
                            console.log('Restoring original options due to AJAX error');
                            attractionField.html(originalAttractionOptions);
                            restaurantField.html(originalRestaurantOptions);
                            hotelField.html(originalHotelOptions);
                        }
                    });
                } else {
                    console.log('No destination selected, restoring original options');
                    // 如果没有选择destination，恢复原始选项
                    attractionField.html(originalAttractionOptions);
                    restaurantField.html(originalRestaurantOptions);
                    hotelField.html(originalHotelOptions);
                }
            });
            
            console.log('Change event bound successfully');
            
            // 页面加载时，如果已经有选择的destination，触发一次change事件
            console.log('Initial destination value:', destinationField.val());
            if (destinationField.val()) {
                console.log('Triggering initial change event');
                destinationField.trigger('change');
            }
        }, 500); // 增加500ms延迟，确保所有元素都已加载
    });
})(django.jQuery);
