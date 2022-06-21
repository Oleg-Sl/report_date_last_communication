def converting_list_to_dict(queryset, key_depth_first=None, key_depth_second=None):
    response = {}
    for element in queryset:
        if not response.get(element[key_depth_first]):
            response[element[key_depth_first]] = {}

        if key_depth_second:
            response[element[key_depth_first]][element[key_depth_second]] = element
        else:
            response[element[key_depth_first]] = element

    return response

