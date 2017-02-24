
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
        actions_str += "<a type='button' class='btn btn-danger btn-sm action-button' href='javascript:void(0);' onclick='delete_metadata(\"" + API_ROOT + "meta" + resource_path + "?key=" + response[idx] +"\")'>";
        actions_str += "<span class='glyphicon glyphicon-remove' aria-hidden='true'></span>  Delete</a>";
        output.push({"key": response[idx], "actions": actions_str})
    }

    return output;
}

function get_metadata(params) {
    // Generate API url
    var resources = get_resource_names();
    $.ajax({
        url: API_ROOT + "meta/" + resources[0] + "/" + resources[1]+ "/" + resources[2],
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

function delete_metadata(url){
    delete_api_call(url, "#metadata_table", "Your metadata item has been deleted")
}