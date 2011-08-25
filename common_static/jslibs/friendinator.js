(function() {
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };
  jQuery.fn.extend({
    friendinator: function(options) {
      options != null ? options : options = {};
      FB.api('/me/friends', __bind(function(response) {
        var friendobjs, items;
        friendobjs = response.data;
        items = [];
        $.each(friendobjs, function(i, friendobj) {
          return items.push({
            label: friendobj.name,
            value: friendobj.id
          });
        });
        return this.each(function(x) {
          return $(this).autocomplete({
            source: items,
            delay: 0,
            select: function(event, ui) {
              $(this).val(ui.item.label);
              if (options.uidElement != null) {
                $(options.uidElement).val(ui.item.value);
              }
              return false;
            },
            focus: function(event, ui) {
              $(this).val(ui.item.label);
              return false;
            }
          });
        });
      }, this));
      return this;
    }
  });
}).call(this);
