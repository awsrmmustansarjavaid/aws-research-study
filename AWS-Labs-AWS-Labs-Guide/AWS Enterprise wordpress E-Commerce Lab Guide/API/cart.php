<?php
require_once('wp-load.php');
header('Content-Type: application/json');

session_start();

$product_id = $_POST['product_id'];
$quantity = $_POST['quantity'];

if (!isset($_SESSION['cart'])) {
    $_SESSION['cart'] = array();
}

$_SESSION['cart'][$product_id] = $quantity;

echo json_encode(array('message' => 'Product added to cart', 'cart' => $_SESSION['cart']));
?>
