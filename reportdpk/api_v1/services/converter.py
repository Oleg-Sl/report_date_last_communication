def converting_list_to_dict(queryset, key_depth_first, key_depth_second):
    response = {}
    for element in queryset:
        if not response.get(element[key_depth_first]):
            response[element[key_depth_first]] = {}

        response[element[key_depth_first]][element[key_depth_second]] = element

    return response

