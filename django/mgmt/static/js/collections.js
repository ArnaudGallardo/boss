
function collection_handler(response) {
    // Reformat
    var output = [];
    for (var idx in response) {
        var actions_str = "<a type='button' class='btn btn-default btn-sm action-button' href=" + window.location.href + "/" + response[idx] + ">";
        actions_str += "<span class='glyphicon glyphicon-pencil' aria-hidden='true'></span>  Details</a>";
        actions_str += "<a type='button' class='btn btn-danger btn-sm action-button' href='javascript:void(0);' onclick='delete_collection(\"" + API_ROOT + "collection/" + response[idx] + "\")'>";
        actions_str += "<span class='glyphicon glyphicon-remove' aria-hidden='true'></span>  Delete</a>";
        output.push({"name": response[idx], "actions": actions_str})
    }

    return output;
}
function coord_handler(response) {
    // Reformat
    var output = [];
    for (var idx in response) {
        var actions_str = "<a type='button' class='btn btn-default btn-sm action-button' href=" + API_ROOT + "mgmt/coord/" + response[idx] + ">";
        actions_str += "<span class='glyphicon glyphicon-pencil' aria-hidden='true'></span>  Details</a>";
        actions_str += "<a type='button' class='btn btn-danger btn-sm action-button' href='javascript:void(0);' onclick='delete_coord_frame(\"" + API_ROOT + "coord/" + response[idx] + "\")'>";
        actions_str += "<span class='glyphicon glyphicon-remove' aria-hidden='true'></span>  Delete</a>";
        output.push({"name": response[idx], "actions": actions_str})
    }

    return output;
}

function experiment_handler(response) {
    // Gen path for delete
    var collection = window.location.pathname.split("/").pop(-1);
    var delete_path_root = API_ROOT + "collection/" + collection + "/experiment/";

    var output = [];
    for (var idx in response) {
        var actions_str = "<a type='button' class='btn btn-default btn-sm action-button' href=" + mgmt_path_root() + "/" + response[idx] + ">";
        actions_str += "<span class='glyphicon glyphicon-pencil' aria-hidden='true'></span>  Details</a>";
        actions_str += "<a type='button' class='btn btn-danger btn-sm action-button' href='javascript:void(0);' onclick='delete_experiment(\"" + delete_path_root + response[idx] + "\")'>";
        actions_str += "<span class='glyphicon glyphicon-remove' aria-hidden='true'></span>  Delete</a>";
        output.push({"name": response[idx], "actions": actions_str})
    }

    return output;
}

function metadata_handler(response) {
    // Reformat
    var output = [];
    var meta_pathname = window.location.pathname.replace("/mgmt/resources", "/mgmt/meta");
    var meta_root = window.location.protocol + "//" + window.location.hostname + meta_pathname;

    var resource_path = window.location.pathname.split("/mgmt/resources")[1];

    for (var idx in response) {
        var actions_str = "<a type='button' class='btn btn-default btn-sm action-button' href='javascript:void(0);' onclick='show_meta_detail(\"" + API_ROOT + "meta" + resource_path + "?key=" + response[idx] +"\")'>";
        actions_str += "<span class='glyphicon glyphicon-eye-open' aria-hidden='true'></span>  View</a>";
        actions_str += "<a type='button' class='btn btn-default btn-sm action-button' href=" + meta_root + "?key=" + response[idx] + ">";
        actions_str += "<span class='glyphicon glyphicon-pencil' aria-hidden='true'></span>  Update</a>";
        //actions_str += "<a type='button' class='btn btn-danger btn-sm action-button' href='" + delete_path_root + "?rem_meta=" + response[idx] + "'>";
        actions_str += "<a type='button' class='btn btn-danger btn-sm action-button' href='javascript:void(0);' onclick='delete_metadata(\"" + API_ROOT + "meta" + resource_path + "?key=" + response[idx] +"\")'>";
        actions_str += "<span class='glyphicon glyphicon-remove' aria-hidden='true'></span>  Delete</a>";
        output.push({"key": response[idx], "actions": actions_str})
    }

    return output;
}

function get_collections(params) {
    $.ajax({
        url: API_ROOT + "collection",
        type: "GET",
        headers: {
            "Accept" : "application/json; charset=utf-8",
            "Content-Type": "application/json; charset=utf-8"
        },
        cache: false,
        statusCode: {
            200: function (response) {
                params.success(response.collections)
            },
            404: function (response) {
                raise_ajax_error(response)
            },
            400: function (response) {
                raise_ajax_error(response)
            },
            403: function (response) {
                raise_ajax_error(response)
            },
            500: function (response) {
                raise_ajax_error(response)
            }
        }
        });
}

function get_experiments(params) {
    // Generate API url
    var collection_name = window.location.pathname.substring(window.location.pathname.lastIndexOf("/") + 1, window.location.pathname.length);
    $.ajax({
        url: API_ROOT + "collection/" + collection_name,
        type: "GET",
        headers: {
            "Accept" : "application/json; charset=utf-8",
            "Content-Type": "application/json; charset=utf-8"
        },
        cache: false,
        statusCode: {
            200: function (response) {
                params.success(response.experiments)
            },
            404: function (response) {
                raise_ajax_error(response)
            },
            400: function (response) {
                raise_ajax_error(response)
            },
            403: function (response) {
                raise_ajax_error(response)
            },
            500: function (response) {
                raise_ajax_error(response)
            }
        }
        });
}

function get_coords(params) {
    $.ajax({
        url: API_ROOT + "coord",
        type: "GET",
        headers: {
            "Accept" : "application/json; charset=utf-8",
            "Content-Type": "application/json; charset=utf-8"
        },
        cache: false,
        statusCode: {
            200: function (response) {
                params.success(response.coords)
            },
            404: function (response) {
                raise_ajax_error(response)
            },
            400: function (response) {
                raise_ajax_error(response)
            },
            403: function (response) {
                raise_ajax_error(response)
            },
            500: function (response) {
                raise_ajax_error(response)
            }
        }
        });
}

function get_metadata(params) {
    // Generate API url
    var collection_name = window.location.pathname.substring(window.location.pathname.lastIndexOf("/") + 1, window.location.pathname.length);
    $.ajax({
        url: API_ROOT + "meta/" + collection_name,
        type: "GET",
        headers: {
            "Accept" : "application/json; charset=utf-8",
            "Content-Type": "application/json; charset=utf-8"
        },
        statusCode: {
            200: function (response) {
                params.success(response.keys)
            },
            404: function (response) {
                raise_ajax_error(response)
            },
            400: function (response) {
                raise_ajax_error(response)
            },
            403: function (response) {
                raise_ajax_error(response)
            },
            500: function (response) {
                raise_ajax_error(response)
            }
        }
        });
}


function delete_collection(url){
    delete_api_call(url, "#collection_table", "Your collection has been marked for deletion")
}
function delete_coord_frame(url){
    delete_api_call(url, "#coord_table", "Your coordinate frame has been marked for deletion")
}
function delete_experiment(url){
    delete_api_call(url, "#experiment_table", "Your experiment has been marked for deletion")
}
function delete_metadata(url){
    delete_api_call(url, "#metadata_table", "Your metadata item has been deleted")
}
