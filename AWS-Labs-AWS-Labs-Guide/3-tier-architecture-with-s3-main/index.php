<?php
require 'vendor/autoload.php';
use Aws\S3\S3Client;

// ==== AWS CONFIG ====
$bucketName = "your-s3-bucket-name";
$cloudfrontDomain = "https://your-cloudfront-id.cloudfront.net";

// ==== RDS CONFIG ====
$host = "your-rds-endpoint";
$db   = "yourdbname";
$user = "yourdbuser";
$pass = "yourdbpassword";

// ==== Collect Form Data ====
$name = $_POST['name'] ?? '';
$age = $_POST['age'] ?? '';
$email = $_POST['email'] ?? '';
$phone = $_POST['phone'] ?? '';
$address = $_POST['address'] ?? '';
$occupation = $_POST['occupation'] ?? '';
$website = $_POST['website'] ?? '';
$description = $_POST['description'] ?? '';

// ==== File Upload to S3 ====
if (isset($_FILES['file']) && $_FILES['file']['error'] === UPLOAD_ERR_OK) {
    $fileTmp = $_FILES['file']['tmp_name'];
    $fileName = uniqid() . "_" . basename($_FILES['file']['name']);

    $s3 = new S3Client([
        'region'  => 'ap-south-1',
        'version' => 'latest',
        'credentials' => [
            'key'    => 'YOUR_AWS_ACCESS_KEY',
            'secret' => 'YOUR_AWS_SECRET_KEY',
        ]
    ]);

    try {
        $result = $s3->putObject([
            'Bucket' => $bucketName,
            'Key'    => $fileName,
            'SourceFile' => $fileTmp,
            'ACL'    => 'public-read'
        ]);

        // CloudFront URL
        $imageUrl = $cloudfrontDomain . "/" . $fileName;

        // ==== Insert into RDS ====
        $pdo = new PDO("mysql:host=$host;dbname=$db", $user, $pass);
        $stmt = $pdo->prepare("INSERT INTO uploads 
          (name, age, email, phone, address, occupation, website, description, image_url) 
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)");
        $stmt->execute([$name, $age, $email, $phone, $address, $occupation, $website, $description, $imageUrl]);

        echo "<h2 style='color:green;text-align:center;'>✅ Data & Image uploaded successfully!</h2>";
        echo "<p style='text-align:center;'><img src='$imageUrl' width='200'></p>";

    } catch (Exception $e) {
        echo "Error: " . $e->getMessage();
    }
} else {
    echo "File upload failed.";
}
?>
