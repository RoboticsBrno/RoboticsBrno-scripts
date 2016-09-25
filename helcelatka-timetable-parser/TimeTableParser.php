<?php

require __DIR__ . '/vendor/autoload.php';

use PHPHtmlParser\Dom;
use Tracy\Debugger;
use Nette\Utils\SafeStream;


class TimeTableParser
{

	public $parseUrl = 'http://www.helceletka.cz/is/www/club/';

	public $baseUrl = "http://www.helceletka.cz";

	//Debugging
	//public $limit = 1692313;

	public $fileName = 'classes.html';


	public function createFile()
	{
		SafeStream::register();

		$page = new Dom;
		$page->load($this->parseUrl);

		$table = new Dom;
		$table->load($page->find('.default'));
		$tableBody = $table->getElementsByTag('tr');

		$isFirst = TRUE;
		$result = "";
		$counter = 0;

		$handle = fopen('nette.safe://' . $this->fileName, 'w');

		foreach ($tableBody as $key => $content) {
			if ($isFirst) {
				$isFirst = FALSE;
				continue;
			}

//			$counter++;
//			if ($counter > $this->limit) {
//				break;
//			}

			$row = new Dom;
			$row->load($content->innerHtml);

			$place = $row->getElementsByClass('pobocka')[0]->innerHtml;

			if($place == 'Robotárna') {
				$name = $row->getElementsByClass('nazev')[0]->find('a')->innerHtml;
				$url = $row->getElementsByClass('nazev')[0]->find('a')->getAttribute('href');

				$this->dump($key . " out of " . (count($tableBody) - 1) . " [Title is " . $name . "]");

//			$handleDebug = fopen('debug.txt', 'a');
//			fwrite($handleDebug, $key);
//			fclose($handleDebug);

				//$result[$key] = $this->createHtmlTemplate([
				$result .= $this->createHtmlTemplate([
					'name' => $name,
					'url' => htmlspecialchars_decode($this->baseUrl . $url),
					'day' => $row->getElementsByClass('dny_konani')[0]->innerHtml,
					'place' => $row->getElementsByClass('pobocka')[0]->innerHtml,
					'description' => $this->getDescription($this->baseUrl . $url),
				]);
				usleep(100);
			}
		};

		fwrite($handle, $result);
		fclose($handle);
	}


	private function getDescription($url)
	{
		$table = new Dom;
		$table->loadFromUrl(htmlspecialchars_decode($url));

		$row = new Dom;
		$row->load($table->find('.popis')[0]);

		return $row->find('.value')[0]->innerHtml;
	}


	private function createHtmlTemplate($data)
	{
		return "
		<h3><a href=\"{$data["url"]}\">{$data["name"]}</a> - {$data["day"]}</h3>
        <p>{$data["description"]}</p>
		";
	}

	private function dump($msg)
	{
		Debugger::dump($msg);
		flush();
	}
}


$table = new TimeTableParser;
$table->createFile();
