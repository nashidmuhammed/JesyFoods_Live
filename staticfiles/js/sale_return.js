

var count = document.getElementById("count");


function calc_amount(){
    for (let i = 1; i<=count.value; i++){

        
        
        document.getElementById('dummy').value = parseFloat(document.getElementById('tot').value) - parseFloat(document.getElementById('amount'+i).value)
        document.getElementById('amount'+i).value =
        parseFloat(document.getElementById('qty'+i).value) * parseFloat(document.getElementById('price'+i).value) ;
        
        
      
        if (isNaN(document.getElementById('amount'+i).value)) {
            document.getElementById('amount'+i).value = 0
          }
        

        document.getElementById('tot').value = parseFloat(document.getElementById('dummy').value) + parseFloat(document.getElementById('amount'+i).value)
    }
}


$('#cancel').click(function(){
    var pr = $('#prefix').val();
    var no = $('#od_no').val();
    var iid = pr+no;
    $('#cancel').attr("disabled", true);
    var action = confirm("Are you sure you want to delete this Sale Return?");
    if (action != false) {
        $.ajax({
                    type: 'GET',
                    url: 'deleteSale',
                    data: {iid:iid},
                    success: function(data) {
                        if (data==1){
                            var oldURL = document.referrer;
                            window.location = oldURL;
                            }
                            else{
                                alert("You are not permission to delete this data!")
                                window.history.go(-1);
                            }
                        },
                    error: function(error) {
                        alert('Something went wrong!\nError Code:RTN-JS5')
                        location.reload();
                        console.log(error);
                    }
                });
            }

    });

$(document).ready(function() {
$("#p_name").change(function(){
    var select = $('#p_name option:selected').val();
    var party = $('#party_name').val();
    console.log('pname :'+select)
    console.log('party :'+party)
        $.ajax({
            type: 'GET',
            url: 'pro_price',
            data: {select:select, party:party},
            success: function(data) {
            console.log('data success='+data)
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
    });
});




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

    $('#add, #add_n').click(function(){
    var party_name = $('#s_party').val();
    var pname = $('#p_name option:selected').val();
    var price = Number($('#price').val());
    var qty = Number($('#qty').val());
    var fqty = Number($('#fqty').val());
    var amount = price * qty;
    var count = Number($('#count').val());
    var total = Number($('#tot').val()) + amount;
    if ( price.length === 0 || price == 0){
        alert('Price Zero');
        return;
        }
    else if (pname === '--Select Product--'){
        alert('Select a Product');
        return;
        }
    var data_id = $(this).data("id");
    $('#add').attr("disabled", true);
    $('#add_n').attr("disabled", true);
    $("#table > tbody:last-child").append(`
            <tr>
                <td class="itemName td"><input name="name${count+1}" readonly class="ed form-control" type="text" value="${pname}"></td>
                '<td class="itemQty td">                
                <input name="qty${count+1}" id="qty${count+1}" class="input-sm qty" type="text" value="${qty}"  oninput="calc_amount()" >
                <input name="fqty${count+1}"  class="input-sm" type="text" value="${fqty}">
              </td>
                '<td class="itemAmt td">₹ <input name="price${count+1}" id="price${count+1}" class="input-sm" type="text" value="${price}" oninput="calc_amount()"> 
                </td>
                <td class="itemAmt td">
                ₹ <input name="amount${count+1}" id="amount${count+1}" class="input-sm" type="text" value="${amount}" readonly> 
                </td>
                '
            </tr>
        `);
    $('#tot').val(total);
    
    $("#p_name").val('--Select Product--');
    $('#select2-p_name-container').html('--Select Product--');
    $('#price').val('');
    $('#qty').val('');
    $('#fqty').val('');
    $('#toot').val('');
    $('#f_price').val('');
    $('#count').val(count + 1);
    if (data_id == 1){
        $('#AddItem').modal('toggle'); 
    }
    $('#add').attr("disabled", false);
    $('#add_n').attr("disabled", false);
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


