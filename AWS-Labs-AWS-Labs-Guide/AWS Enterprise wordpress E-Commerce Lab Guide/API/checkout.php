<?php
require_once('wp-load.php');
header('Content-Type: application/json');

session_start();

if (!isset($_SESSION['cart']) || empty($_SESSION['cart'])) {
    echo json_encode(array('error' => 'Cart is empty'));
    exit;
}

// Here you could integrate payment gateway or order creation
$order_status = 'success';
$order_id = rand(1000, 9999); // Sample order ID

// Clear cart
$_SESSION['cart'] = array();

echo json_encode(array('message' => 'Order placed', 'order_id' => $order_id, 'status' => $order_status));
?>
