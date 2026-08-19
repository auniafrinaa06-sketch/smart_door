<?php
$servername = "localhost";
$username = "root"; 
$password = "";     
$dbname = "smart_door_db";
$port = 3307; // <--- DAH TAMBAH PORT 3307 KAT SINI

// Masukkan $port di hujung sekali
$conn = new mysqli($servername, $username, $password, $dbname, $port);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $uid = $_POST['uid'];
    $status = $_POST['status'];
    $user = isset($_POST['username']) ? $_POST['username'] : 'Unknown';

    $sql = "INSERT INTO access_log (uid_card, username, status) VALUES ('$uid', '$user', '$status')";

    if ($conn->query($sql) === TRUE) {
        echo "Data berjaya dimasukkan!";
    } else {
        echo "Error: " . $sql;
    }
} else {
    echo "Sistem sedia menerima data.";
}

$conn->close();
?>