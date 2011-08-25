jQuery.fn.extend
    friendinator: (options) ->
        options ?= {}

        # Get this persons friends
        FB.api '/me/friends', (response) =>
            friendobjs = response.data

            items = []
            $.each friendobjs, (i, friendobj) ->
                items.push
                    label:friendobj.name
                    value:friendobj.id

            @each (x) ->
                $(this).autocomplete
                    source: items
                    delay: 0
                    select: (event, ui) ->
                        $(this).val(ui.item.label)
                        if options.uidElement?
                            $(options.uidElement).val(ui.item.value)
                        return false
                    focus: (event, ui) ->
                        $(this).val(ui.item.label)
                        return false
        return this
