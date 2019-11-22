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

pool.getConnection(function(err, connection) {
    // Use the connection
    connection.query('SELECT * from Cluster', function (error, results, fields) {
        // And done with the connection.
        connection.release();
        // Handle error after the release.
        if (error) throw error;
        else console.log(results[0].densidad_trafico);
        process.exit();
    });
});