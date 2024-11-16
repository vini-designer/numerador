var contador_arq = 1;

function prox_fls(num_container, num_fl){
    var div_grid = document.createElement("DIV");

    div_grid.innerHTML = '<input class="fl_input" type="text" id="cont' + num_container + '_fl' + (num_fl + 1) + '" name="cont' + num_container + '_fl" title="Página ' + (num_fl + 1) + '" maxlength="3" min="1" max="250"/>';
    document.getElementById("container_fls" + num_container).appendChild(div_grid);
}

/*function novo_arq(){
    var div_arq = document.createElement("DIV");
    contador_arq+=1;

    div_arq.innerHTML = '<div id="container_fls' + contador_arq.toString() + '" style="display: grid; grid-template-columns: repeat(7, 35px); justify-content: center; row-gap: 5px; column-gap: 5px;"></div><div style="display: flex; justify-content: center;"><input class="form-control" type="file" id="arquivo' + contador_arq.toString() + '" onchange="add_field(this)" style="width: 280px; margin-top: 10px; margin-bottom: 20px;"></div>';
    document.getElementById("container_arq").appendChild(div_arq);
}*/

function add_field(num_pgs){
    for (let i = 0; i < num_pgs; i++) {
        prox_fls(1, i);
    }
    document.getElementById("cont1_fl1").focus();
    document.getElementById("cont1_fl1").select();
}    