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

        // var day = date.getDate();
        // var month = date.getMonth() + 1;
        // var year = date.getFullYear();

        // if (month < 10) month = "0" + month;
        // if (day < 10) day = "0" + day;

        // var today = year + "-" + month + "-" + day;
        // if ($("#date").val() == ''){
        // $("#date").attr("value", today);
        // }
        $("#add_btn").attr("disabled", true);
        $("#add_rpt").attr("disabled", true);
        $(".total").hide();
        $('.alert').hide();
        $('#inp_report').hide();

        if ($('#s_party').val() !== '-----Select a Party-----'){
            $("#add_btn").attr("disabled", false);
            $("#add_rpt").attr("disabled", false);
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
           $('#fn-load').show();
           var select = $('#p_name option:selected').val();
           var party = $('#s_party option:selected').val();
               $.ajax({
                type: 'GET',
                url: 'pro_price',
                data: {select:select, party:party},
                success: function(data) {
                $('#fn-load').hide();
                if (data == 'none'){
                     alert('Please select a Product')
                     }
                else{
                    $('#price').val(data.l_price);
                    $('#f_price').val(data.price);
                    }
                    },
                error: function(error) {
                    alert('Something went wrong!\nError Code:ASL-JS1')
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
    var d_id = $(this).data("id");
    var rc = 0;
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
                url: 'add_purchase_item',
                data: {rc:rc,party_name:party_name,pname:pname,price:price,qty:qty,fqty:fqty,od_no:od_no,date:date,prefix:prefix},
                success: function(data) {
                    $('#fn-load').hide();
                    if (data.msg == 1){
                        console.log('if data ='+data)
                        alert('Error: Invoice no. already exists! Try again...')
                        location.reload();
                        return;
                    }
                    if (data.stock == 1){
                        //$('#table tr:last').after('<tr><td>'+data.pname+'</td><td>'+data.qty+'</td><td>₹'+data.amt+'</td></tr>');
                        console.log('table row added')
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
                    alert('Something went wrong!\nError Code:ASL-JS2')
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
                        $('#ed_delete').show();
                        $('#toot').val(data.amt);
                        $('#AddItemLongTitle').html('Edit Item');
                        $('#itm_id').val(data.id);

                        //$('#close').hide();
                        //$('#toot').val( parseInt(data.price)*parseInt(data.qty));
                    },
                error: function(error) {
                    alert('Something went wrong!\nError Code:ASL-JS3')
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
                    url: 'delete_sale_item',
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
                        alert('Something went wrong!\nError Code:ASL-JS4')
                        location.reload();
                        console.log(error);
                    }
                });
        }
    });


    $('#save-sale, #save-new').click(function(){
    var od_no = $('#od_no').val();
    console.log('od_no:'+od_no)
    var pr = $('#prefix').val();
    console.log('prefix:'+pr)
    var rc = $('#rc').val();
    var type = $('#p-type').val();
    var d_id = $(this).data("id");
    var date = $('#date').val();
    var report = $('#report').val();
    $('#save-sale').attr("disabled", true);
    $('#save-new').attr("disabled", true);
    $('#fn-load').show();
    $.ajax({
                type: 'GET',
                url: 'saveSale',
                data: {od_no:od_no, pr:pr, rc:rc, type:type,date:date,report:report},
                success: function(data) {
                        $('#fn-load').hide();
                        if (data == 1){
                            if (d_id == 2){
                                window.location.href = 'add_sale';
                            }
                            else{
                                var path = $(location).attr('search');
                                console.log('path='+path)
                                if (path == ''){
                                    window.location.href = 'home';
                                }
                                else{
                                    window.history.go(-1);
                                }
                            }
                        }
                        else{
                            $('#alt-save').show();
                            $('#alt-save').delay( 5000 ).fadeOut();
                       
                        }
                    },
                error: function(error) {
                    $('#fn-load').hide();
                    alert('Something went wrong!\nError Code:ASL-JS5')
                    location.reload();
                    console.log(error);
                }
            });

    });

    $('#cancel').click(function(){
    var pr = $('#prefix').val();
    var no = $('#od_no').val();
    var iid = pr+no;
    var action = confirm("Are you sure you want to delete this Sale?");
    if (action != false) {
        $('#fn-load').show();
        $.ajax({
                    type: 'GET',
                    url: 'deleteSale',
                    data: {iid:iid},
                    success: function(data) {
                        $('#fn-load').hide();
                        if (data){
                            window.location.href = 'sale_report';
                            }
                        },
                    error: function(error) {
                        $('#fn-load').hide();
                        alert('Something went wrong!\nError Code:ASL-JS6')
                        location.reload();
                        console.log(error);
                    }
                });
            }

    });

    $('#add_report').click(function(){
    var party_name = $('#s_party').val();
    var rpt = $('#rpt').val();
    $.ajax({
                type: 'GET',
                url: 'add_report',
                data: {party_name:party_name,rpt:rpt},
                success: function(data) {
                        $('#AddReport').modal('toggle');
                        $('#alt-rpt').show();
                        $('#alt-rpt').delay( 5000 ).fadeOut();
                    },
                error: function(error) {
                    alert('Something went wrong!\nError Code:ASL-JS7')
                    location.reload();
                    console.log(error);
                }
            });

    });



    $('#add_btn').click(function(){
        $('#ed_delete').hide();
        //$('#close').show();
        $("#p_name").val('--Select Product--');
        $('#select2-p_name-container').html('--Select Product--');
        $('#price').val('');
        $('#qty').val('');
        $('#fqty').val('');
        $('#f_price').val('');
        $('#toot').val('');
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
    