
  $(document).ready(function() {
              $('#update').hide()
              $('#edit').click(function () {
                         $('.ed').attr("disabled", false);
                         $('#update').show();
                         $('#edit').hide()
                      });

        $("#sub").click(function(){
        var staff = $('#s_party option:selected').val();
        var amount = $('#amount').val();
        var p_type = $('#p_type option:selected').val();
        if (amount == '' || staff == '--Select a staff---'){
            alert('Cannot submit without amount & Staff')
            return;
        }
            $.ajax({
             type: 'GET',
             url: 'take_collection',
             data: {staff:staff,amount:amount,p_type:p_type},
             success: function(data) {
             console.log('data success='+data)
                $('#takeCollection').modal('toggle');
                location.reload();
                 },
             error: function(error) {
                 console.log(error);
             }
         });
     })

            });

$(document).ready(function() {
    $('input[type="checkbox"]').click(function(){
            if($(this).prop("checked") == true){
                console.log("Checkbox is checked.");
                var data = ($(this).attr("data-id"));
                var value = 'true'
                console.log("Checkbox idd=."+data);
            }
            else if($(this).prop("checked") == false){
                console.log("Checkbox is unchecked.");
                var data = ($(this).attr("data-id"));
                var value = ''
                console.log("Checkbox idd="+data);
            }
            $.ajax({
                type: 'GET',
                url: 'active_product',
                data: {data:data, value:value},
                success: function(data) {
                    if (data){
                        console.log('saved ')

                    }
                    else{
                        alert('Something went wrong! ERROR DLTODR-2')
                    }

                        //$('#close').hide();
                        //$('#toot').val( parseInt(data.price)*parseInt(data.qty));
                    },
                error: function(error) {
                    console.log(error);
                }
            });
        });



        $('#minus, #plus').click(function(){
            var data = ($(this).attr("data-id"));
            var res = $('#res').html()
            console.log('res ='+res)
            if (data == 0){
                res = parseInt(res-1)
                if (res < 0){
                    res = 0
                }
                $('#res').html(res)
            }
            else if (data == 1){
                res = parseInt(res)+parseInt(1)
                $('#res').html(res)
            }
            console.log('wor')
            $.ajax({
                type: 'GET',
                url: 'settings',
                data: {data:res, value:'column'},
                success: function(data) {
                    if (data){
                        console.log('saved ')

                    }
                    else{
                        alert('Something went wrong! ERROR DLTODR-2')
                    }

                        //$('#close').hide();
                        //$('#toot').val( parseInt(data.price)*parseInt(data.qty));
                    },
                error: function(error) {
                    console.log(error);
                }
            });
        });

  });