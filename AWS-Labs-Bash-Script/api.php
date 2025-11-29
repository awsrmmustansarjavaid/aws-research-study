<?php
// --- CORS SETTINGS ---
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type");
header("Content-Type: application/json");

// OPTIONS request for browser preflight
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// --- Database credentials ---
$host = "ecommerce-static-site-db.cm5oowikel4z.us-east-1.rds.amazonaws.com";
$db   = "ecommerce";
$user = "admin";
$pass = "admin987";

// Connect DB
$conn = new mysqli($host, $user, $pass, $db);
if ($conn->connect_error) {
    http_response_code(500);
    echo json_encode(["error" => "Database connection failed"]);
    exit();
}

// Query database
$sql = "SELECT * FROM products";
$result = $conn->query($sql);

$products = [];
while ($row = $result->fetch_assoc()) {
    $products[] = $row;
}

// Return JSON
echo json_encode($products);

$conn->close();
?>
