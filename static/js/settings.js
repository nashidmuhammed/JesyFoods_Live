


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
                url: 'settings',
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