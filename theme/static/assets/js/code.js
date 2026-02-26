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
    var group_file   = '.xlsx, .xlsm';
    var myDropzone = null;

    function dropZone(domaine){
        maxFile = 1;
        group_file   = '.xlsx, .xlsm';

        // const myDropzone = new Dropzone("#my-dropzone", {
        //     url: "upload",
        //     maxFiles: maxFile,
        //     maxFilesize: 15,
        //     acceptedFiles: group_file,
        //     addRemoveLinks: true
        // });

        if (myDropzone) {
            myDropzone.removeAllFiles(true);
            myDropzone.options.maxFiles = 1;
            myDropzone.options.acceptedFiles = '.xlsx, .xlsm';
            return;
        }

        myDropzone = new Dropzone("#my-dropzone", {
            url: "upload",
            maxFiles: 1,
            maxFilesize: 15,
            acceptedFiles: '.xlsx, .xlsm',
            addRemoveLinks: true
        });
    };

    //     function initDropzone() {
    //     if (myDropzone) {
    //         myDropzone.removeAllFiles(true);
    //         return;
    //     }

    //     myDropzone = new Dropzone(SELECTORS.dropzone, {
    //         url: "upload",
    //         maxFiles: 1,
    //         maxFilesize: 15,
    //         acceptedFiles: ".xlsx, .xlsm",
    //         addRemoveLinks: true
    //     });
    // }



    function updateTyDocSelect(docs, selected = null) {
        const $select = $("#apply select[name='ty_doc']");

        // On enlève UNIQUEMENT ce que le JS a ajouté
        $select.find('option.dyn-tydoc').remove();

        let html = '';
        docs.forEach(doc => {
            html += `<option class="dyn-tydoc" value="${doc.id}" ${
                selected && selected === doc.id ? 'selected' : ''
            }>${doc.label}</option>`;
        });

        $select.append(html);
    }

    function ajaxProgramSelect(ll_context, url){
        $.ajax({
            url: url,
            type: 'GET',
            dataType: "json",
            success: function(response) {
                var option = '';
                for (var i = 0; i < response.dataPro.id.length; i++) {
                    if (!ll_context.programme) {
                       option += '<option value="' + response.dataPro.id[i] + '">' + response.dataPro.value[i] + '</option>';
                    } else {
                       if (ll_context.programme == response.dataPro.id[i]) {
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
    }


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
                // console.log(ll_context.domaine)
                ajaxProgramSelect(ll_context, '/palangre')

                updateTyDocSelect(
                    [
                        { id: "ll_17.6", label: "SFA logbook version 17.6" },
                        { id: "ll_26",   label: "SFA logbook version 26" }
                    ],
                    ll_context.ty_doc
                );

            } else if (ll_context.domaine == "senne") {
                ajaxProgramSelect(ll_context, '/senne')

                updateTyDocSelect(
                    [
                        { id: "ps", label: "Logbook ORTHONGEL v21" },
                        { id: "ps2", label: "Logbook ORTHONGEL v23" },
                        { id: "ers",   label: "Données ERS" }
                    ],
                    ll_context.ty_doc
                );
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

        updateTyDocSelect([]);

        if ($this.val() == "senne") {

            updateTyDocSelect([
                { id: "ps", label: "Logbook ORTHONGEL v21" },
                { id: "ps2", label: "Logbook ORTHONGEL v23" },
                { id: "ers",   label: "Données ERS" }
            ]);

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

        }else if ($this.val() == "palangre") {

            // $("#apply select[name='ty_doc']").find('.after').after('<option value="ll">Logbook  SFA industriel</option>');
            
            updateTyDocSelect([
                { id: "ll_17.6", label: "SFA logbook version 17.6" },
                { id: "ll_26",   label: "SFA logbook version 26" }
            ]);
            
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

        if (($("#domaine").val() != "" ) && ($("#programme").val() != "" ) && ($("#ocean").val() != "" ) && ($("#ty_doc").val() != "" )) {
            // console.log($("#apply").serialize());
            data = $("#apply").serialize();
            // console.log($("#apply").data("url"));
            //  POURQUOI ? On peut juste faire si ce n'est pas ERS => Oui c'est vrai
            if (($("#apply select[name='ty_doc']").val() == "ps") || ($("#apply select[name='ty_doc']").val() == "ps2") || ($("#apply select[name='ty_doc']").val() == "ll_17.6") || ($("#apply select[name='ty_doc']").val() == "ll_26")){

                
                if (myDropzone) {
                    myDropzone.disable();   // stop tout
                    myDropzone.destroy();   // 🔥 ferme TOUS les handles Windows
                    myDropzone = null;
                }

                

                $("#div_ers").hide(1500);

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
            else if ($("#apply select[name='ty_doc']").val() == "ers"){

                /**
                 * Formate une date ISO (ex: 2025-06-30T06:48:00)
                 * en format lisible : YYYY-MM-DD HH:mm
                 */
                function formatDateISO(dateStr) {
                    if (!dateStr) return "";

                    const date = new Date(dateStr);

                    const year = date.getFullYear();
                    const month = String(date.getMonth() + 1).padStart(2, '0');
                    const day = String(date.getDate()).padStart(2, '0');

                    const hours = String(date.getHours()).padStart(2, '0');
                    const minutes = String(date.getMinutes()).padStart(2, '0');

                    return `${year}-${month}-${day} à ${hours}:${minutes}`;
                }

                $("#div_upload").hide(1500);

                // Code ajax faisant reference la fonction "postProg_info" de la vue qui permet de sauvegarder au niveau des variables de session
                // les infos (domaine, ocean, programme et ty_doc)
                $.ajax({
                        type: 'POST',
                        url: $("#apply").attr('action'), // reference la fonction "postProg_info"
                        data: data,
                        dataType: "json",
                        success: function(response){
                            if (response.message == 'success'){
                                // Code ajax pour afficher les données ERS si nous sommes connectés au VPN et à la base Postgres des données ERS
                                $.ajax({
                                        type: 'POST',
                                        url: 'ERSloadData', // reference la fonction "ERSloadData"
                                        data: data,
                                        dataType: "json",
                                        success: function(result){
                                            // console.log(result.connectBool)
                                            if (result.connectBool === true) {
                                                // Vider la liste avant de remplir
                                                $("#ers_list").empty();

                                                // Parcourir les données ERS reçues
                                                $.each(result.dataTripERS, function(index, trip){

                                                    let li_html = `
                                                        <li class="ers-item flex items-center justify-between px-6 py-5 hover:bg-gray-50 cursor-pointer"
                                                            data-trip-id="${trip.trip_id}">

                                                            <div class="min-w-0 w-full">

                                                                <!-- TITRE -->
                                                                <div class="flex items-center gap-3">
                                                                    <p class="font-semibold text-gray-900 truncate">
                                                                        ${trip.trip_vessel_name}
                                                                    </p>
                                                                    <span class="inline-flex mt-3items-center gap-2 text-sm text-gray-500">
                                                                        (${trip.trip_captain_name})
                                                                    </span>
                                                                    <span class="inline-flex items-center rounded-md bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">
                                                                        Complete
                                                                    </span>
                                                                </div>

                                                                <!-- META -->
                                                                <div class="mt-3 flex items-center gap-2 text-sm text-gray-500">
                                                                    <span>${formatDateISO(trip.trip_start_date)}</span>
                                                                    <span class="font-semibold">(${trip.trip_departure_harbour_name})</span>
                                                                    <span>•</span>
                                                                    <span class="truncate">${formatDateISO(trip.trip_end_date)}</span>
                                                                    <span class="font-semibold">(${trip.trip_landing_harbour_name})</span>
                                                                </div>

                                                                <!-- SOUS INFOS (cachées) -->
                                                                <div class="sous_info_li hidden mt-5 w-full"></div>

                                                            </div>
                                                        </li>
                                                    `;

                                                    $("#ers_list").append(li_html);
                                                });

                                                $("#div_ers").show(1500);
                                            }
                                            else{
                                                $("#div_ers").hide(1500);
                                                Swal.fire({
                                                      icon: "error",
                                                      title: "Oops...",
                                                      text: result.message,
                                                      // footer: '<a href="#">Why do I have this issue?</a>'
                                                    });
                                                console.log(result.message);
                                            }
                                        },
                                        error: function(result){
                                            cconsole.log("Erreur au niveau de la requête ERSloadData");
                                        }
                                });

                            }else{
                                console.log(response.message);
                            }
                        },
                        error: function(response){
                            console.log('La configuration n\'a pas été enregistrée');
                        }
                });
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

    /**
     * Gestion du clic sur un élément ERS (<li>)
     */
    $(document).on('click', '.ers-item', function (e) {

        // Si le clic vient d'un bouton → on ignore
        if ($(e.target).closest('.btn-insert, .btn-update').length) {
            return;
        }

        // <li> cliqué
        let currentLi = $(this);

        // trip_id (clé unique)
        let tripId = currentLi.data('trip-id');

        // div sous-infos du <li> cliqué
        let currentSubInfo = currentLi.find('.sous_info_li');

        /**
         * Fermer tous les autres blocs ouverts
         */
        $('.sous_info_li').not(currentSubInfo).slideUp(500).empty();

        /**
         * Si déjà ouvert → on ferme et on sort
         */
        if (currentSubInfo.is(':visible')) {
            currentSubInfo.slideUp(500);
            return;
        }

        /**
         * Loader simple pendant l'appel AJAX
         */
        currentSubInfo.html(`
            <div class="text-sm text-red-400">
                Chargement des détails...
            </div>
        `).slideDown(500);

        /**
         * Appel AJAX vers Django
         */
        $.ajax({
            type: 'GET',
            url: `/logbook/ERSloadTripDetails/${tripId}/`,
            dataType: 'json',
            success: function (response) {

                if (response.connectBool === true) {

                    let d = response.data;

                    /**
                     * HTML des sous-infos de la marée ERS
                     */
                    let sousInfoHtml = `
                        <div class="sous_info_li_actuel">

                            <div class="info_maree flex gap-4 font-semibold text-sm text-black">
                                <div>
                                    <span class="text-blue-500">Nombre d'Activités :</span>
                                    <span>${d.num_activity}</span>
                                </div>
                                |
                                <div>
                                    <span class="text-blue-500">Activités de Pêche :</span>
                                    <span>${d.num_fishing_activity}</span>
                                </div>
                                |
                                <div>
                                    <span class="text-blue-500">Débarquements :</span>
                                    <span>${d.num_landing}</span>
                                </div>
                                |
                                <div>
                                    <span class="text-blue-500">Rejets :</span>
                                    <span>${d.num_discards}</span>
                                </div>

                                <div class="gap-4 ml-20">
                                    <a href="#"
                                       class="btn-insert mr-3 rounded-md bg-blue-300 px-3 py-2 text-xs font-semibold ring-1 ring-gray-300 hover:bg-blue-500"
                                       data-trip-id="${tripId}">
                                        Insérer les données
                                    </a>

                                    <a href="#"
                                       class="btn-update rounded-md bg-gray-200 px-3 py-2 text-xs font-semibold ring-1 ring-gray-300 hover:bg-gray-500"
                                       data-trip-id="${tripId}">
                                        Mettre à jour les données
                                    </a>
                                </div>
                            </div>

                        </div>
                    `;

                    currentSubInfo.html(sousInfoHtml);

                } else {
                    currentSubInfo.html(
                        `<div class="text-red-500 text-sm">${response.message}</div>`
                    );
                }
            },
            error: function () {
                currentSubInfo.html(
                    `<div class="text-red-500 text-sm">Erreur lors du chargement</div>`
                );
            }
        });
    });

    // Bloque toute l'interface utilisateur
    function lockUI() {
        $('#ui-lock-overlay').removeClass('hidden');
        $('body').addClass('overflow-hidden'); // empêche l'utilisateur de scroller
    }

    // Débloque toute l'interface utilisateur
    function unlockUI() {
        $('#ui-lock-overlay').addClass('hidden');
        $('body').removeClass('overflow-hidden');
    }

    /**
     * Gestion clic sur "Insérer" ou "Mettre à jour" ERS
     */
    $(document).on('click', '.btn-insert, .btn-update', function (e) {
        e.preventDefault();
        e.stopPropagation(); // STOP propagation du clique vers le <li> pour eviter qu'il se ferme

        // Verrouiller toute l'interface
        lockUI();

        // Bouton cliqué
        let btn = $(this);

        // trip_id concerné
        let tripId = btn.data('trip-id');

        // Zone message ERS globale
        let messageZone = $('#ers_message_zone');

        // Nettoyer anciens messages
        messageZone.hide().empty();

        // Désactiver les boutons pendant le traitement
        $('.btn-insert, .btn-update').addClass('pointer-events-none opacity-50').prop('disabled', true);

        /**
         * Appel AJAX vers Django
         */
        $.ajax({
            type: 'POST',
            url: `/logbook/sendERSDATA/${tripId}/`,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function (response) {

                let alertHtml = '';

                if (response.message === 'Success') {

                    if (response.code === 1) {
                        // Succès
                        alertHtml = `
                            <div class="bg-teal-100 border-t-4 border-teal-500 text-teal-900 px-4 py-3 rounded">
                                <strong>Succès :</strong> ${response.msg}
                            </div>
                        `;
                    } else if (response.code === 2) {
                        // Erreur bloquante
                        alertHtml = `
                            <div class="bg-red-100 border-t-4 border-red-500 text-red-900 px-4 py-3 rounded">
                                <strong>Erreur :</strong> ${response.msg}
                            </div>
                        `;
                    } else {
                        // Warning
                        alertHtml = `
                            <div class="bg-yellow-100 border-t-4 border-yellow-500 text-yellow-900 px-4 py-3 rounded">
                                <strong>Attention :</strong> ${response.msg}
                            </div>
                        `;
                    }

                } else {
                    alertHtml = `
                        <div class="bg-red-100 border-t-4 border-red-500 text-red-900 px-4 py-3 rounded">
                            Une erreur est survenue.
                        </div>
                    `;
                }

                // Affichage message ERS
                messageZone.html(alertHtml).slideDown(300);
            },

            error: function () {
                messageZone.html(`
                    <div class="bg-red-100 border-t-4 border-red-500 text-red-900 px-4 py-3 rounded">
                        Erreur de communication avec le serveur.
                    </div>
                `).slideDown(300);
            },

            complete: function () {
                // Déverrouiller l'interface (QUOI QU'IL ARRIVE)
                unlockUI();

                // Réactiver boutons
                $('.btn-insert, .btn-update').removeClass('pointer-events-none opacity-50').prop('disabled', false);
            }
        });
    });

    // Fermer messages ERS lors du changement de trip
    $('#ers_message_zone').slideUp(200).empty();

    // Fermer les messages ERS si on clique ailleurs
    $(document).on('click', function (e) {

        // Si le clic ne vient PAS d'un bouton ERS
        if (!$(e.target).closest('.btn-insert, .btn-update').length) {
            $('#ers_message_zone').slideUp(200);
        }
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
                        $(".message").find('.aft').after('<div id="msg">'+ response.msg +'</div>');
                        $('.btn_error').show();
                    }else{
                        $(".message").find('.aft').after('<div class="flex p-4 mb-4 bg-yellow-100 border-t-4 border-yellow-500 dark:bg-yellow-200" role="alert"><div class="ml-3 text-sm font-medium text-red-700"><p class="font-bold">Attention</p><br><p>'+ response.msg +'</p></div></div>');
                        $('.btn_warning').show();
                    }
                }else{
                    console.log("Probleme");
                }
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

    function bindLoadDataButton(buttonId) {
        $(`#${buttonId}`).click(function(e) {
            e.preventDefault();
            $(".message").hide(1500);
            $("#div_upload").show(1500);

            const url = $(this).data('url');
            $.ajax({
                type: 'POST',
                url: url,
                data: $("#form_test").serialize(),
                success: function(response) {
                    const domaine = response.domaine;
                    dropZone(domaine);
                }
            });
            $(this).hide(1500);
        });
    };

    for (let i = 1; i <= 8; i++) {
        bindLoadDataButton(`load_data${i}`);
    };
    console.log("terminé");

});

