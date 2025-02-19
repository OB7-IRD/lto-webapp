Dropzone.autoDiscover = false

$(document).ready(function(){

    /*
    setTimeout(function(){
       if($('.card').length > 0){
            $('.card').remove();
       }
    },180000);



    setTimeout(function(){
       if($('#msg2').length > 0){
            $('#msg2').remove();
       }
    },10000);
    */

    var maxFile = 1;
    var group_file   = '.xlsx, .xlsm, .zip';

    function dropZone(domaine){
        if (domaine == "senne"){
             maxFile = 1;
             group_file   = '.xlsx, .xlsm';
        }else{
             maxFile = 1;
             group_file   = '.xlsx, .xlsm, .zip';
        }

        const myDropzone = new Dropzone("#my-dropzone", {
            url: "upload",
            maxFiles: maxFile,
            maxFilesize: 15,
            acceptedFiles: group_file,
        });
    };

    // Récupération des données du contexte via le script JSON intégré
    let scriptElement = document.getElementById('context-data');
    let ll_context = null;
    try {
        let rawData = scriptElement.text || scriptElement.textContent;
        ll_context = JSON.parse(rawData);

        // Vérifiez si l'élément existe
        if (ll_context) {
            if (ll_context.ocean) {
                $("#ocean").val(ll_context.ocean); // Applique la valeur sélectionnée pour l'océan
            }
            if (ll_context.domaine) {
                $("#domaine").val(ll_context.domaine);
            }
            if (ll_context.domaine == "palangre") {
                console.log(ll_context.domaine)
                $.ajax({
                    url: '/palangre',
                    type: 'GET',
                    dataType: "json",
                    success: function(response) {
                        var option = '';
                        for (var i = 0; i < response.dataPro.id.length; i++) {
                            if (!ll_context.programme) {
                                option += '<option value="' + response.dataPro.id[i] + '">' + response.dataPro.value[i] + '</option>';
                            } else {
                                if (ll_context.programme == response.dataPro.id[i]) {
                                    $("#apply select[name='ty_doc']").find('.after').after('<option selected value="ll">Logbook SFA industriel</option>');
                                    option += '<option selected value="' + response.dataPro.id[i] + '">' + response.dataPro.value[i] + '</option>';
                                } else {
                                    option += '<option value="' + response.dataPro.id[i] + '">' + response.dataPro.value[i] + '</option>';
                                }
                            }
                        }
                        $("#apply select[name='programme']").find('.after').after(option);
                    },
                    error: function(response) {
                        console.log('Erreur lors de la requête AJAX');
                    }
                });

            } else if (ll_context.domaine == "senne") {
                $.ajax({
                    url: '/senne',
                    type: 'GET',
                    dataType: "json",
                    success: function(response) {
                        var option = '';
                        for (var i = 0; i < response.dataPro.id.length; i++) {
                            if (!ll_context.programme) {
                                option += '<option value="' + response.dataPro.id[i] + '">' + response.dataPro.value[i] + '</option>';
                            } else {
                                if (ll_context.programme == response.dataPro.id[i]) {
                                    // console.log(ll_context);
                                    if (ll_context.ty_doc == "ps"){
                                        $("#apply select[name='ty_doc']").find('.after').after('<option selected class="orth" value="ps">Logbook ORTHONGEL v21</option>');
                                        $("#apply select[name='ty_doc']").find('.orth').after('<option class="orth23" value="ps2">Logbook ORTHONGEL v23</option>');
                                    }else{
                                        $("#apply select[name='ty_doc']").find('.after').after('<option class="orth" value="ps">Logbook ORTHONGEL v21</option>');
                                        $("#apply select[name='ty_doc']").find('.orth').after('<option selected class="orth23" value="ps2">Logbook ORTHONGEL v23</option>');
                                    };
                                    $("#apply select[name='ty_doc']").find('.orth23').after('<option class="ers" value="ers">Données ERS</option>');

                                    option += '<option selected value="' + response.dataPro.id[i] + '">' + response.dataPro.value[i] + '</option>';
                                } else {
                                    option += '<option value="' + response.dataPro.id[i] + '">' + response.dataPro.value[i] + '</option>';
                                }
                            }
                        }
                        $("#apply select[name='programme']").find('.after').after(option);
                    },
                    error: function(response) {
                        console.log('Erreur lors de la requête AJAX');
                    }
                });
            };
        }
    }
    catch(err) {
      contextElement = null;
      console.log("L'élément avec l'ID 'context-data' n'existe pas.");
    };

    $("#domaine").change(function(){
        // console.log($(this).val());
        $this = $(this);
        $("#apply select[name='ty_doc']").find('.after').nextAll().remove();
        $("#apply select[name='programme']").find('.after').nextAll().remove();

        if ($this.val() == "senne") {

            $("#apply select[name='ty_doc']").find('.after').after('<option class="orth" value="ps">Logbook ORTHONGEL v21</option>');
            $("#apply select[name='ty_doc']").find('.orth').after('<option class="orth23" value="ps2">Logbook ORTHONGEL v23</option>');
            $("#apply select[name='ty_doc']").find('.orth23').after('<option class="ers" value="ers">Données ERS</option>');
            $.ajax({
                url: '/'+ $this.val(),
                type: 'GET',
                success: function(response){
                    // maxFile = 2;
                    // group_file   = '.xlsx, .xlsm';

                    let option = '';
                    for (var i = 0; i < response.dataPro.id.length; i++) {
                        //println(response.dataPro.id[i]);
                        option += '<option value='+response.dataPro.id[i]+'>'+response.dataPro.value[i]+'</option>';
                    }
                    $("#apply select[name='programme']").find('.after').after(option);
                },
                error: function(response){
                    console.log('Rien');
                }
            });
            //$("#apply").append('<option value="{{ key }}">{{ value }}</option>');

        }else if ($this.val() == "palangre") {

            $("#apply select[name='ty_doc']").find('.after').after('<option value="ll">Logbook  SFA industriel</option>');
            $.ajax({
                url: '/'+$this.val(),
                type: 'GET',
                success: function(response){
                    // maxFile = 2;
                    // group_file   = '.xlsx, .xlsm';

                    let option = '';
                    for (var i = 0; i < response.dataPro.id.length; i++) {
                        option += '<option value='+response.dataPro.id[i]+'>'+response.dataPro.value[i]+'</option>';
                    }
                    $("#apply select[name='programme']").find('.after').after(option);
                },
                error: function(response){
                    console.log('Rien');
                }
            });
            // $("#apply").append('<option value="{{ key }}">{{ value }}</option>');
        }else{
            $("#apply select[name='ty_doc']").find('.after').nextAll().remove();
        }
    });

    $("#btn_apply").click(function(e){
        e.preventDefault();

        if (($("#domaine").val() != "Domaine..." ) && ($("#programme").val() != "Programmes du domaine..." ) && ($("#ocean").val() != "Ocean..." ) && ($("#ty_doc").val() != "Types de document..." )) {
            // console.log($("#apply").serialize());
            data = $("#apply").serialize();
            // console.log($("#apply").data("url"));
            if (($("#apply select[name='ty_doc']").val() == "ps") || ($("#apply select[name='ty_doc']").val() == "ps2") || ($("#apply select[name='ty_doc']").val() == "ll")){

                $.ajax({
                    type: 'POST',
                    url: 'del_files',
                    data: data,
                    dataType: "json",
                    success: function(response){
                        console.log(" Bien ");
                    },
                    error: function(response){
                        console.log('erreur de suppression');
                    }
                });

                if ($("#apply select[name='ty_doc']").val() == "ps"){
                    $.ajax({
                        type: 'POST',
                        url: $("#apply").attr('action'),
                        data: data,
                        dataType: "json",
                        success: function(response){

                            if (response.message == 'success'){
                                console.log("Configuration enregistrée vous pouvez faire la migration des données logbook");

                            }else{
                                console.log("2message unsuccess"+response.message);
                            }
                        },
                        error: function(response){
                            console.log('La configuration n\'a pas été enregistrer');
                        }
                    });
                    $("#div_upload").show(1500);
                    $("#my-dropzone button[class='dz-button']").text('Drop files here to upload and extract data');

                    var domaine = $("#domaine").val();
                    dropZone(domaine);
                }

                else if ($("#apply select[name='ty_doc']").val() == "ps2"){
                    $.ajax({
                        type: 'POST',
                        url: $("#apply").attr('action'),
                        data: data,
                        dataType: "json",
                        success: function(response){

                            if (response.message == 'success'){
                                console.log("Configuration enregistrée vous pouvez faire la migration des données logbook");

                            }else{
                                console.log("2message unsuccess"+response.message);
                            }
                        },
                        error: function(response){
                            console.log('La configuration n\'a pas été enregistrer');
                        }
                    });
                    $("#div_upload").show(1500);
                    $("#my-dropzone button[class='dz-button']").text('Drop files here to upload and extract data');

                    var domaine = $("#domaine").val();
                    dropZone(domaine);
                }

                // palangre
                else if ($("#apply select[name='ty_doc']").val() == "ll"){
                    $.ajax({
                        type: 'POST',
                        url: $("#apply").attr('action'),
                        data: data,
                        dataType: "json",
                        success: function(response){

                            if (response.message == 'success'){
                                console.log("Configuration enregistrée vous pouvez faire la migration des données logbook");

                            }else{
                                console.log(response.message);
                            }
                        },
                        error: function(response){
                            console.log('La configuration n\'a pas été enregistrée');
                        }
                    });
                    $("#div_upload").show(1500);
                    $("#my-dropzone button[class='dz-button']").text('Drop files here to upload and extract data');

                    var domaine = $("#domaine").val();
                    dropZone(domaine);
                }
            }
            else if ($("#apply select[name='ty_doc']").val() == "ers"){
                $("#div_upload").hide(1500);
                console.log('Rien pour l\'instant ');

            }
            console.log('Affiche le domaine'+$("#apply select[name='ty_doc']").val());

        }else{
            Swal.fire({
              icon: "error",
              title: "Oops...",
              text: 'Merci de selectionner tous les champs avant d\'appliquer',
              // footer: '<a href="#">Why do I have this issue?</a>'
            });
        }
    });

    $("#my-dropzone button[class='dz-button']").click(function(e){
        e.preventDefault();
        console.log($("#my-dropzone").serialize());
    });

    $('#load_data').click(function(e){
        e.preventDefault();
        $(".message").hide(1500);
        $("#div_upload").show(1500);

        $.ajax({
          type: 'POST',
          url: $('#load_data').data('url'),
          data: $("#form_test").serialize(),
          success: function(response){
            var domaine = response.domaine;
            dropZone(domaine);
          }
        });
    });

    $('#load_data2').click(function(e){
        e.preventDefault();
        $(".message").hide(1500);
        $("#div_upload").show(1500);

        $.ajax({
          type: 'POST',
          url: $('#load_data2').data('url'),
          data: $("#form_test").serialize(),
          success: function(response){
            var domaine = response.domaine;
            dropZone(domaine);
          }
        });
    });

    $('#load_data3').click(function(e){
        e.preventDefault();
        $(".message").hide(1500);
        $("#div_upload").show(1500);

        $.ajax({
          type: 'POST',
          url: $('#load_data3').data('url'),
          data: $("#form_test").serialize(),
          success: function(response){
            var domaine = response.domaine;
            dropZone(domaine);
          }
        });

    });

    $('#load_data7').click(function(e){
        e.preventDefault();
        $(".message").hide(1500);
        $("#div_upload").show(1500);

        $.ajax({
          type: 'POST',
          url: $('#load_data7').data('url'),
          data: $("#form_test").serialize(),
          success: function(response){
            var domaine = response.domaine;
            dropZone(domaine);
          }
        });

    });

    $('#cancel_btn').click(function(e){
        // e.preventDefault();

        var mDropzone = Dropzone.forElement("#my-dropzone");
        mDropzone.removeAllFiles(true);

        $.ajax({
            type: 'POST',
            url: $('#cancel_btn').data('url'),
            data: $("#form_test").serialize(),
            success: function(response){
                console.log("OK dom et fil")
            }
        });

        console.log('Reset dropZone');
    });

    $('#send_data').click(function(e){
        e.preventDefault();
        $(".spinner_info").show();
        $.ajax({
          type: 'POST',
          url: $(this).data('url'),
          data: $("#form_test").serialize(),
          success: function(response){
                // $(".message").hide(1500);
                $(".message").find('.aft').nextAll().remove();
                if(response.message == 'Success'){
                    if (response.code == 1){
                        $(".message").find('.aft').after('<div class="bg-teal-100 border-t-4 border-teal-500 rounded-b text-teal-900 px-4 py-3 shadow-md" role="alert"><div class="flex"><div class="py-1"><svg class="fill-current h-6 w-6 text-teal-500 mr-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M2.93 17.07A10 10 0 1 1 17.07 2.93 10 10 0 0 1 2.93 17.07zm12.73-1.41A8 8 0 1 0 4.34 4.34a8 8 0 0 0 11.32 11.32zM9 11V9h2v6H9v-4zm0-6h2v2H9V5z"/></svg></div><div><p class="font-bold">Effectué</p><p class="text-sm">'+ response.msg +'</p></div></div></div><br>');
                        $('.btn_success').show();
                    }else if (response.code == 2){
                        $(".message").find('.aft').after('<div class="flex p-4 mb-4 bg-red-100 border-t-4 border-red-500 dark:bg-red-200" id="msg" role="alert"><div class="ml-3 text-sm font-medium text-red-700"><p class="font-bold">Erreur</p><br><p>'+ response.msg +'</p></div></div>');
                        $('.btn_error').show();
                    }else{
                        $(".message").find('.aft').after('<div class="flex p-4 mb-4 bg-yellow-100 border-t-4 border-yellow-500 dark:bg-yellow-200" role="alert"><div class="ml-3 text-sm font-medium text-red-700"><p class="font-bold">Attention</p><br><p>'+ response.msg +'</p></div></div>');
                        $('.btn_warning').show();
                    }
                }else{
                    console.log("Probleme");
                }
                // $("#div_upload").hide(1500);
                // date heure ==> Information non conforme sur le ou les FOB de l'activité:  - visite
                // Nombre total d'erreurs tout types confondus: nb_error
                // Mise a jour faite à heure
                // ******** Les données concernant les espèces rejetées sont mauvaises. ==> le 2021-05-27 00:00:00 à 07:20:00 ==> // Date heure ==> Les données concernant les espèces rejetées sont mal formatées (raison exacte indeterminée)
                // Date heure ==> les especes rejetees doivent etre indiquees avec leur code FAO (ASFIS) 3 lettres. Le code trouvé est: code_logbook
          },
          error: function(response){

          }
        });
    });

    $('#send_data2').click(function(e){
        e.preventDefault();
        $(".spinner_error").show();
        $.ajax({
          type: 'POST',
          url: $(this).data('url'),
          data: $("#form_test").serialize(),
          success: function(response){
                // $(".message").hide(1500);
                $(".message").find('.aft').nextAll().remove();
                if(response.message == 'Success'){
                    if (response.code == 1){
                        $(".message").find('.aft').after('<div class="bg-teal-100 border-t-4 border-teal-500 rounded-b text-teal-900 px-4 py-3 shadow-md" role="alert"><div class="flex"><div class="py-1"><svg class="fill-current h-6 w-6 text-teal-500 mr-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M2.93 17.07A10 10 0 1 1 17.07 2.93 10 10 0 0 1 2.93 17.07zm12.73-1.41A8 8 0 1 0 4.34 4.34a8 8 0 0 0 11.32 11.32zM9 11V9h2v6H9v-4zm0-6h2v2H9V5z"/></svg></div><div><p class="font-bold">Effectué</p><p class="text-sm">'+ response.msg +'</p></div></div></div><br>');
                        $('.btn_success').show();
                    }else if (response.code == 2){
                        $(".message").find('.aft').after('<div class="flex p-4 mb-4 bg-red-100 border-t-4 border-red-500 dark:bg-red-200" id="msg" role="alert"><div class="ml-3 text-sm font-medium text-red-700"><p class="font-bold">Erreur</p><br><p>'+ response.msg +'</p></div></div>');
                        $('.btn_error').show();
                    }else{
                        $(".message").find('.aft').after('<div class="flex p-4 mb-4 bg-yellow-100 border-t-4 border-yellow-500 dark:bg-yellow-200" role="alert"><div class="ml-3 text-sm font-medium text-red-700"><p class="font-bold">Attention</p><br><p>'+ response.msg +'</p></div></div>');
                        $('.btn_warning').show();
                    }
                }else{
                    console.log("Probleme");
                }
                // $("#div_upload").hide(1500);
          },
          error: function(response){

          }
        });
    });

    $('#load_data4').click(function(e){
        e.preventDefault();
        $(".card").hide(1500);
        $("#div_upload").show(1500);

        $.ajax({
          type: 'POST',
          url: $('#load_data4').data('url'),
          data: $("#form_test").serialize(),
          success: function(response){
            var domaine = response.domaine;
            dropZone(domaine);
          }
        });

    });

    $('#load_data5').click(function(e){
        e.preventDefault();
        $(".card").hide(1500);
        $("#div_upload").show(1500);

        $.ajax({
          type: 'POST',
          url: $('#load_data5').data('url'),
          data: $("#form_test").serialize(),
          success: function(response){
            var domaine = response.domaine;
            dropZone(domaine);
          }
        });

    });

    $('#load_data6').click(function(e){
        e.preventDefault();
        $(".card").hide(1500);
        $("#div_upload").show(1500);

        $.ajax({
          type: 'POST',
          url: $('#load_data6').data('url'),
          data: $("#form_test").serialize(),
          success: function(response){
            var domaine = response.domaine;
            dropZone(domaine);
          }
        });

    });
});