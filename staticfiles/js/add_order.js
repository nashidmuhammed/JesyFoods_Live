var text1 = document.getElementById("price");
var text2 = document.getElementById("qty");
var tot = document.getElementById("toot");

function add_number() {
   var first_number = parseFloat(text1.value);
   if (isNaN(first_number)) first_number = 0;
   var second_number = parseFloat(text2.value);
   if (isNaN(second_number)) second_number = 0;
   var result = first_number * second_number;
   console.log('result='+result);
   document.getElementById("toot").value = result;
}
function tot_number() {
    var first_number = parseFloat(text2.value);
    if (isNaN(first_number)) first_number = 0;
    var second_number = parseFloat(tot.value);
    if (isNaN(second_number)) second_number = 0;
    var result = second_number / first_number;
    console.log('result='+result);
    document.getElementById("price").value = result;
 }

  $(document).ready(function() {
        // var date = new Date();

        // var day = date.getDate() + 1;
        // var month = date.getMonth() + 1;
        // var year = date.getFullYear();

        // if (month < 10) month = "0" + month;
        // if (day < 10) day = "0" + day;

        // var today = year + "-" + month + "-" + day;
        // console.log('date ='+today)
        // if ($("#date").val() == ''){
        // $("#date").attr("value", today);
        // }
        $("#add_btn").hide();
        $("#add_pay").hide();
        $("#add_rpt").hide();
        $(".total").hide();
        $('.alert').hide();
        $('#inp_report').hide();

        if ($('#s_party').val() !== '-----Select a Party-----'){
            $("#add_btn").show();
            $("#add_pay").show();
            $("#add_rpt").show();
            $(".total").show();
            $('#inp_report').show();
            $("#cancel").children('p').html('Delete');
        }
        });

     $(document).ready(function() {
     $('#s_party').change(function(){
        $('#form1').submit()

      });


        $("#p_name").change(function(){
           var select = $('#p_name option:selected').val();
           var party = $('#s_party option:selected').val();
           $('#fn-load').show();
               $.ajax({
                type: 'GET',
                url: 'pro_price',
                data: {select:select, party:party},
                success: function(data) {
                console.log('data success='+data)
                $('#fn-load').hide();
                if (data.price == 'none'){
                     alert('Please select a Product')
                     }
                else{
                    $('#price').val(data.l_price);
                    $('#f_price').val(data.price);
                    }
                    },
                error: function(error) {
                    alert('Something went wrong!\nError Code:AOD-JS1')
                    location.reload();
                    console.log(error);
                }
            });
        })
    });

    $('#add, #add_n').click(function(){
    var party_name = $('#s_party').val();
    var pname = $('#p_name option:selected').val();
    var price = $('#price').val();
    var qty = $('#qty').val();
    var fqty = $('#fqty').val();
    var od_no = $('#od_no').val();
    var date = $('#date').val();
    var prefix = $('#prefix').val();
    var d_id = $(this).data("id")
    console.log('DATA ID ++='+d_id)
    if ( price.length === 0 || price == 0){
        alert('Price Zero');
        return;
        }
    else if (pname === '--Select Product--'){
        alert('Select a Product');
        return;
        }
    $('#add').attr("disabled", true);
    $('#add_n').attr("disabled", true);
    $('#fn-load').show();
    $.ajax({
                type: 'GET',
                url: 'add_order_item',
                data: {party_name:party_name,pname:pname,price:price,qty:qty,fqty:fqty,od_no:od_no,date:date,prefix:prefix},
                success: function(data) {
                    $('#fn-load').hide();
                    if (data.msg == 1){
                        console.log('if data ='+data)
                        alert('Error: Order no. already exists! Try again...')
                        location.reload();
                        return;
                    }
                    if (data.stock == 1){
                        appendToUsrTable(data);
                        $('#tot').val(data.tot);
                        $('#cb').val(parseFloat($('#tot').val())+parseFloat($('#ob').val()))
                        if (d_id == 2){
                            $("#p_name").val('--Select Product--');
                            $('#select2-p_name-container').html('--Select Product--');
                            $('#price').val('');
                            $('#qty').val('');
                            $('#fqty').val('');
                            $('#toot').val('');
                            $('#f_price').val('');
                            console.log('cleareddd');
                        }
                        else{
                            $('#AddItem').modal('toggle');
                        }
                        $('#add').attr("disabled", false);
                        $('#add_n').attr("disabled", false);
                    }
                    else if(data.stock == 2){
                        //alert('Item Updated')
                        updateToItemTabel(data);
                        $('#tot').val(data.tot);
                        $('#cb').val(parseFloat($('#tot').val())+parseFloat($('#ob').val()))
                        if (d_id == 2){
                            $("#p_name").val('--Select Product--');
                            $('#select2-p_name-container').html('--Select Product--');
                            $('#price').val('');
                            $('#qty').val('');
                            $('#fqty').val('');
                            $('#toot').val('');
                            $('#f_price').val('');
                            console.log('cleareddd');
                        }
                        else{
                            $('#AddItem').modal('toggle');
                        }
                        $('#add').attr("disabled", false);
                        $('#add_n').attr("disabled", false);
                    }
                    else{
                        alert('Something went wrong! ERROR ADITM01');
                        $('#add').attr("disabled", false);
                        $('#add_n').attr("disabled", false);
                        $('#toot').val('');

                        }
                    },
                error: function(error) {
                    $('#fn-load').hide();
                    alert('Something went wrong!\nError Code:AOD-JS2')
                    location.reload();
                    console.log(error);
                }
            });

    });

    function appendToUsrTable(data) {
        $("#table > tbody:last-child").append(`
                <tr id="item-${data.id}">
                    <td class="itemName td" name="name"><a onClick="editItem(${data.id})" data-toggle="modal" data-target="#AddItem")>${data.pname}</a></td>
                    '<td class="itemQty td" name="qty">${data.qty}</td>
                    '<td class="itemAmt td" name="amt">${data.amt}</td>
                    '
                </tr>
            `);
        }
    function editItem(id) {
      $('#fn-load').show();
      if (id) {
        tr_id = id;
        $.ajax({
                type: 'GET',
                url: 'edit_sale_item',
                data: {tr_id:tr_id},
                success: function(data) {
                        $('#fn-load').hide();
                        $('#p_name').val(data.itm);
                        $('#select2-p_name-container').html(data.itm);
                        $('#price').val(data.price);
                        $('#qty').val(data.qty);
                        $('#fqty').val(data.fqty);
                        $('#f_price').val(data.f_price);
                        $('#ed_delete').show();
                        $('#toot').val(data.amt);
                        $('#AddItemLongTitle').html('Edit Item');
                        $('#itm_id').val(data.id);

                        //$('#close').hide();
                        //$('#toot').val( parseInt(data.price)*parseInt(data.qty));
                    },
                error: function(error) {
                    alert('Something went wrong!\nError Code:AOD-JS3')
                    location.reload();
                    console.log(error);
                }
            });
      }
    }
    function updateToItemTabel(data){
    console.log('Entered data='+data)
    console.log('Entered data id='+data.id)
        $("#table #item-" + data.id).children(".td").each(function() {
    console.log('Entered 2')
            var attr = $(this).attr("name");
            console.log('atrr='+attr)
            if (attr == "name") {
              $(this).empty().append(`
              <a onClick="editItem(${data.id})" data-toggle="modal" data-target="#AddItem")>${data.pname}</a>`
              );
            } else if (attr == "qty") {
              $(this).text(data.qty);
            } else {
              $(this).text(data.amt);
            }
          });
          console.log('sucess updateToItemTabel')
    }

 $('#ed_delete').click(function(){
    var itm_id = $('#itm_id').val();
    var action = confirm("Are you sure you want to delete this Item?");
    if (action != false) {
        $('#fn-load').show();
        $.ajax({
                    type: 'GET',
                    url: 'delete_order_item',
                    data: {itm_id:itm_id},
                    success: function(data) {
                            $('#fn-load').hide();
                            if (data.deleted) {
                              $("#table #item-" + itm_id).remove();
                              $('#AddItem').modal('toggle');
                              $('#tot').val(data.tot);
                              $('#cb').val(parseFloat($('#tot').val())+parseFloat($('#ob').val()))
                            }
                        },
                    error: function(error) {
                        $('#fn-load').hide();
                        alert('Something went wrong!\nError Code:AOD-JS4')
                        location.reload();
                        console.log(error);
                    }
                });
        }
    });


    $('#save-sale, #save-new').click(function(){
    var date = $('#date').val();
    var od_no = $('#od_no').val();
    console.log('od_no:'+od_no)
    var pr = $('#prefix').val();
    console.log('prefix:'+pr)
    var d_id = $(this).data("id");
    var rc = 0
    var report = $('#report').val();
    console.log('rc='+rc)

    $('#save-sale').attr("disabled", true);
    $('#save-new').attr("disabled", true);
    $('#fn-load').show();
    $.ajax({
                type: 'GET',
                url: 'saveSale',
                data: {date:date,od_no:od_no, pr:pr, rc:rc,report:report},
                success: function(data) {
                        $('#fn-load').hide();
                        if (data == 1){
                            if (d_id == 2){
                                window.location.href = 'add_order';
                            }
                            else{
                                // window.history.go(-1);
                                // var path = $(location).attr('search');
                                // console.log('path='+path)
                                // if (path == ''){
                                //     window.location.href = 'home';
                                // }
                                // else{
                                //     window.history.go(-1);
                                // }
                                var oldURL = document.referrer;
                                window.location = oldURL;
                            }
                        }
                        else{
                            $('#alt-save').show();
                            $('#alt-save').delay( 5000 ).fadeOut();
                       
                        }
                    },
                error: function(error) {
                    $('#fn-load').hide();
                    alert('Something went wrong!\nError Code:AOD-JS5')
                    location.reload();
                    console.log(error);
                }
            });

    });

    $('#cancel').click(function(){
    var pr = $('#prefix').val();
    var no = $('#od_no').val();
    var id = 1
    var iid = pr+no;
    var action = confirm("Are you sure you want to delete this order?");
    if (action != false) {
        $('#fn-load').show();
        $.ajax({
                    type: 'GET',
                    url: 'deleteOrder',
                    data: {iid:iid,id:id},
                    success: function(data) {
                        $('#fn-load').hide();
                        if (data){
                            var oldURL = document.referrer;
                            window.location = oldURL;
                            // if ($('#s_party').val() !== '-----Select a Party-----'){
                            //     window.history.go(-2);
                            // }
                            // else{
                            //     window.history.go(-1);
                            // }
                            }
                        },
                    error: function(error) {
                        $('#fn-load').hide();
                        alert('Something went wrong!\nError Code:AOD-JS5')
                        location.reload();
                        console.log(error);
                    }
                });
            }

    });



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
                $('#fn-load').hide();
                 alert('Something went wrong!\nError Code:HM-JS2')
                 location.reload();
                 console.log(error);
             }
         });
     })



    $('#add_btn').click(function(){
        $('#ed_delete').hide();
        //$('#close').show();
        $("#p_name").val('--Select Product--');
        $('#select2-p_name-container').html('--Select Product--');
        $('#price').val('');
        $('#qty').val('');
        $('#fqty').val('');
        $('#toot').val('');
        $('#f_price').val('');
        $('#AddItemLongTitle').html('Add Item');
    });


    /*---------------------------------------------------------------------*/

/*
    $('#add_n').click(function(){
    var party_name = $('#s_party').val();
    var pname = $('#p_name option:selected').val();
    var price = $('#price').val();
    var qty = $('#qty').val();
    var fqty = $('#fqty').val();
    var od_no = $('#od_no').val();
    var date = $('#date').val();
    if ( price.length === 0 || price == 0){
        alert('Price not be Zero');
        return;
        }
    else if (pname === '--Select Product--'){
        alert('Select a Product');
        return;
        }
    $('#add_n').attr("disabled", true);
    $('#add').attr("disabled", true);
    $.ajax({
                type: 'GET',
                url: 'add_item',
                data: {party_name:party_name,pname:pname,price:price,qty:qty,fqty:fqty,od_no:od_no,date:date},
                success: function(data) {
                    if (data.stock == 1){
                        location.reload();
                    }
                    if (data != 'none'){
                        $("#p_name").val('--Select Product--');
                        $('#select2-p_name-container').html('--Select Product--');
                        $('#price').val('');
                        $('#qty').val('');
                        $('#fqty').val('');
                        $('#toot').val('');
                        console.log('cleareddd');
                        $('#add_n').attr("disabled", false);
                        $('#add').attr("disabled", false);
                        }
                    else{
                        alert('Something went wrong! ERROR ADITM01');
                        $('#add_n').attr("disabled", false);
                        $('#add').attr("disabled", true);
                        $('#toot').val('');

                        }
                    },
                error: function(error) {
                    console.log(error);
                }
            });

    });





    $('#cancel').click(function(){
    var party_name = $('#s_party').val();
    $.ajax({
                type: 'GET',
                url: 'del_order',
                data: {party_name:party_name},
                success: function(data) {
                    if (data == 1){
                        alert("Added products unsaved!")
                        }
                    },
                error: function(error) {
                    console.log(error);
                }
            });

    });



    $(document).on('click', "a.ed", function(){
    var itm = $(this).text();
    var party_name = $('#s_party').val();
    console.log('id = '+itm);
    console.log('partyname = '+party_name)
    $.ajax({
                type: 'GET',
                url: 'edit_item',
                data: {party_name:party_name,itm:itm},
                success: function(data) {
                        $('#p_name').val(itm);
                        $('#select2-p_name-container').html(itm);
                        $('#price').val(data.price);
                        $('#qty').val(data.qty);
                        $('#fqty').val(data.fqty);
                        $('#ed_delete').show();
                        $('#close').hide();
                        $('#toot').val( parseInt(data.price)*parseInt(data.qty));
                    },
                error: function(error) {
                    console.log(error);
                }
            });

    });

*/

    //Adm add order
    