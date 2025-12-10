<?php
$db = new SQLite3('places.db');
$results = $db->query('SELECT * FROM places');
$data = [];

while ($row = $results->fetchArray(SQLITE3_ASSOC)) {
  $row['types'] = explode(',', $row['types']);
  $data[] = $row;
}

header('Content-Type: application/json');
echo json_encode($data);
