/**
 * Created by fmaralv on 10/11/19.
 */

var mysql = require('mysql');
var config = require('./config.json');

var pool  = mysql.createPool({
    host     : config.dbhost,
    user     : config.dbuser,
    password : config.dbpassword,
    database : config.dbname
});


exports.handler=  (event, context, callback) => {
    //prevent timeout from waiting event loop
    context.callbackWaitsForEmptyEventLoop = false;

    console.info("EVENT\n" + JSON.stringify(event, null, 2))



    pool.getConnection(function(err, connection) {
        // Use the connection
        connection.query('SELECT Cluster.latitud, Cluster.longitud, predict.ocu_real, predict.ocu_pred  FROM predict INNER JOIN Cluster ON predict.cluster = Cluster.id_cluster WHERE predict.fecha BETWEEN str_to_date(\''+ event['fecha_ini'] + '\', \'%d/%m/%Y %H:%i\') AND str_to_date(\'' + event['fecha_fin'] + '\', \'%d/%m/%Y %H:%i\')', function (error, results, fields) {

            //
            // And done with the connection.
            connection.release();
            connection.destroy();


            // Handle error after the release.
            if (error) {
                callback(error);
            }else{
                callback(null,results);
            }
        });
    });
};
