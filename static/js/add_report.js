//  $("#sub_repor").click(function(){
//     var select = $('#s_party option:selected').val();
//     var rsn = $('#rsn option:selected').val();
//     var disc = $('#disc').val();
//     var cat = $("input[name='inlineRadioOptions']:checked").val()
//     console.log("'caaaaat ===="+cat);
//     if (select == '-----Select a Party-----' || rsn == '-----'){
//         alert('Select currect options!')
//         return;
//     }
//         $.ajax({
//          type: 'GET',
//          url: 'add_report',
//          data: {select:select,rsn:rsn,disc:disc,cat:cat},
//          success: function(data) {
//          console.log('data success='+data)
//             $('#AddReport').modal('toggle');
//             $('#alert').show();
//             $('#msg').html('Report submitted successfully');
//              },
//          error: function(error) {
//             alert('Something went wrong!\nError Code:ARP-JS1')
//             location.reload();
//             console.log(error);
//          }
//      });
//  })


$("input[name='inlineRadioOptions']").change(function(){        
    var cat = $("input[name='inlineRadioOptions']:checked").val()
    console.log("'caaaaat ===="+cat);
    if (cat == 'Feedback'){
        $('#rsn').hide()
    }
    else{
        $('#rsn').show()
    }
});



$("#sub_repor").click(function(){
var select = $('#s_party option:selected').val();
var rsn = $('#rsn option:selected').val();
var disc = $('#disc').val();
var cat = $("input[name='inlineRadioOptions']:checked").val()
console.log("'caaaaat ===="+cat);
if (select == '-----Select a Party-----' || rsn == '-----' && cat == 'Report'){
    alert('Select currect options!')
    return;
}
$('#fn-load').show();
    $.ajax({
     type: 'GET',
     url: 'add_report',
     data: {select:select,rsn:rsn,disc:disc,cat:cat},
     success: function(data) {
        $('#fn-load').hide();
        $('#AddReport').modal('toggle');
        $('#alert').show();
        $('#msg').html('Report submitted successfully');
         },
     error: function(error) {
         alert('Something went wrong!\nError Code:HM-JS2')
         location.reload();
         console.log(error);
     }
 });
})
