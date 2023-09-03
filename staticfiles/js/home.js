$('#day_filter').change(function(){
    $('#form1').submit()

  }); 

  $(document).ready(function() {

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

$("#sub_exp").click(function(){
    var exp = $('#exp option:selected').val();
    var amount = $('#amount').val();
    var disc = $('#disc_expence').val();
    if (amount == ''){
        alert('Cannot submit without amount')
        return;
    }
    $("#sub_exp").attr("disabled", true);
    $('#fn-load').show();
        $.ajax({
         type: 'GET',
         url: 'add_expense',
         data: {exp:exp,amount:amount,disc:disc},
         success: function(data) {
            $('#fn-load').hide();
            $('#AddExpence').modal('toggle');
            $("#sub_exp").attr("disabled", false);
            $('#alert').show();
            $('#msg').html('Expense submitted successfully');
             },
         error: function(error) {
            alert('Something went wrong!\nError Code:HM-JS3')
            location.reload();
            console.log(error);
         }
     });
 })

 $("#sub").click(function(){
    var staff = $('#cs_party option:selected').val();
    var amount = $('#c_amount').val();
    var p_type = $('#p_type option:selected').val();
    if (amount == '' || staff == '--Select a staff---'){
        alert('Cannot submit without amount & Staff')
        return;
    }
    $('#fn-load').show();
        $.ajax({
         type: 'GET',
         url: 'take_collection',
         data: {staff:staff,amount:amount,p_type:p_type},
         success: function(data) {
            $('#fn-load').hide();
            $('#takeCollection').modal('toggle');
            location.reload();
             },
         error: function(error) {
            alert('Something went wrong!\nError Code:HM-JS4')
            location.reload();
            console.log(error);
         }
     });
 })

 $("#delNot").click(function(){
    var id = $('#Nid').val();
        $.ajax({
         type: 'GET',
         url: 'add_alert',
         data: {id:id},
         success: function(data) {
             },
         error: function(error) {
             alert('Something went wrong!\nError Code:ALT-01')
             console.log(error);
         }
     });
 })

});

