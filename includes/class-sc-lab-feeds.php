<?php
if (!defined('ABSPATH')) { exit; }

class SC_Lab_Feeds {
    public static function registry() {
        return array(
            'usgs-earthquakes' => array('label'=>'USGS Earthquakes','domain'=>'Earth science','kind'=>'event','official'=>true),
            'nasa-eonet' => array('label'=>'NASA EONET Natural Events','domain'=>'Earth science','kind'=>'event','official'=>true),
            'nasa-space-telescopes' => array('label'=>'NASA Space Telescope Releases','domain'=>'Astronomy','kind'=>'observation','official'=>true),
            'obis-marine' => array('label'=>'OBIS Marine Biodiversity','domain'=>'Marine biology','kind'=>'occurrence','official'=>true),
            'pubmed-science' => array('label'=>'PubMed Natural Science','domain'=>'Life and chemical sciences','kind'=>'literature','official'=>true),
            'arxiv-physics' => array('label'=>'arXiv Physics and Engineering','domain'=>'Physics, materials and engineering','kind'=>'literature','official'=>true),
        );
    }

    public static function fetch($source, $params = array()) {
        $limit = max(1, min(30, isset($params['limit']) ? absint($params['limit']) : 12));
        switch ($source) {
            case 'usgs-earthquakes': return self::usgs($limit, $params);
            case 'nasa-eonet': return self::eonet($limit, $params);
            case 'nasa-space-telescopes': return self::nasa_images($limit, $params);
            case 'obis-marine': return self::obis($limit, $params);
            case 'pubmed-science': return self::pubmed($limit, $params);
            case 'arxiv-physics': return self::arxiv($limit, $params);
            default: return new WP_Error('unknown_source', 'Unknown scientific source.', array('status'=>404));
        }
    }

    private static function remote_json($url, $args = array()) {
        $args = wp_parse_args($args, array('timeout'=>18, 'headers'=>array('Accept'=>'application/json','User-Agent'=>'SustainableCatalystLab/0.1.0')));
        $response = wp_safe_remote_get($url, $args);
        if (is_wp_error($response)) { return $response; }
        $code = wp_remote_retrieve_response_code($response);
        if ($code < 200 || $code >= 300) { return new WP_Error('source_http_error', 'Scientific source returned HTTP ' . $code, array('status'=>502)); }
        $data = json_decode(wp_remote_retrieve_body($response), true);
        if (!is_array($data)) { return new WP_Error('source_parse_error', 'Scientific source returned invalid data.', array('status'=>502)); }
        return $data;
    }

    private static function record($id, $source, $domain, $title, $summary, $observed, $url, $extra = array()) {
        return array_merge(array(
            'id' => sanitize_text_field((string) $id),
            'source' => $source,
            'domain' => $domain,
            'title' => wp_strip_all_tags((string) $title),
            'summary' => wp_strip_all_tags((string) $summary),
            'observedAt' => $observed,
            'retrievedAt' => gmdate('c'),
            'url' => esc_url_raw($url),
            'provenance' => array('source'=>$source, 'retrievedAt'=>gmdate('c')),
        ), $extra);
    }

    private static function usgs($limit, $params) {
        $days = max(1, min(30, isset($params['days']) ? absint($params['days']) : 7));
        $minmag = isset($params['minMagnitude']) ? floatval($params['minMagnitude']) : 2.5;
        $url = add_query_arg(array('format'=>'geojson','orderby'=>'time','limit'=>$limit,'starttime'=>gmdate('Y-m-d', time()-DAY_IN_SECONDS*$days),'minmagnitude'=>$minmag), 'https://earthquake.usgs.gov/fdsnws/event/1/query');
        $data = self::remote_json($url);
        if (is_wp_error($data)) { return $data; }
        $items = array();
        foreach ((array) ($data['features'] ?? array()) as $feature) {
            $p = $feature['properties'] ?? array(); $coords = $feature['geometry']['coordinates'] ?? array();
            $items[] = self::record($feature['id'] ?? wp_generate_uuid4(), 'USGS', 'Earth science', $p['title'] ?? 'Earthquake event', 'Magnitude ' . ($p['mag'] ?? 'unknown') . '; depth ' . (isset($coords[2]) ? $coords[2] . ' km' : 'unknown'), !empty($p['time']) ? gmdate('c', intval($p['time']/1000)) : null, $p['url'] ?? '', array('type'=>'earthquake','location'=>array('longitude'=>$coords[0] ?? null,'latitude'=>$coords[1] ?? null,'depthKm'=>$coords[2] ?? null),'metrics'=>array('magnitude'=>$p['mag'] ?? null)));
        }
        return $items;
    }

    private static function eonet($limit, $params) {
        $days = max(1, min(180, isset($params['days']) ? absint($params['days']) : 30));
        $url = add_query_arg(array('status'=>'open','days'=>$days,'limit'=>$limit), 'https://eonet.gsfc.nasa.gov/api/v3/events');
        $data = self::remote_json($url);
        if (is_wp_error($data)) { return $data; }
        $items = array();
        foreach ((array) ($data['events'] ?? array()) as $event) {
            $geo = !empty($event['geometry']) ? end($event['geometry']) : array(); $coords = $geo['coordinates'] ?? array();
            $cats = array_map(function($c){ return $c['title'] ?? ''; }, (array) ($event['categories'] ?? array()));
            $items[] = self::record($event['id'] ?? wp_generate_uuid4(), 'NASA EONET', 'Earth science', $event['title'] ?? 'Natural event', implode(', ', array_filter($cats)), $geo['date'] ?? null, !empty($event['sources'][0]['url']) ? $event['sources'][0]['url'] : 'https://eonet.gsfc.nasa.gov/', array('type'=>'natural_event','location'=>array('longitude'=>$coords[0] ?? null,'latitude'=>$coords[1] ?? null),'categories'=>$cats));
        }
        return $items;
    }

    private static function nasa_images($limit, $params) {
        $query = sanitize_text_field(isset($params['q']) ? $params['q'] : 'James Webb Hubble space telescope nebula galaxy');
        $url = add_query_arg(array('q'=>$query,'media_type'=>'image'), 'https://images-api.nasa.gov/search');
        $data = self::remote_json($url);
        if (is_wp_error($data)) { return $data; }
        $items = array();
        foreach (array_slice((array) ($data['collection']['items'] ?? array()), 0, $limit) as $item) {
            $meta = $item['data'][0] ?? array(); $links = $item['links'] ?? array();
            $items[] = self::record($meta['nasa_id'] ?? wp_generate_uuid4(), 'NASA Image and Video Library', 'Astronomy', $meta['title'] ?? 'Space telescope release', $meta['description_508'] ?? ($meta['description'] ?? ''), $meta['date_created'] ?? null, 'https://images.nasa.gov/details/' . rawurlencode($meta['nasa_id'] ?? ''), array('type'=>'space_telescope_release','thumbnail'=>esc_url_raw($links[0]['href'] ?? ''),'keywords'=>$meta['keywords'] ?? array()));
        }
        return $items;
    }

    private static function obis($limit, $params) {
        $scientific = sanitize_text_field(isset($params['scientificName']) ? $params['scientificName'] : 'Cetacea');
        $url = add_query_arg(array('scientificname'=>$scientific,'size'=>$limit), 'https://api.obis.org/v3/occurrence');
        $data = self::remote_json($url);
        if (is_wp_error($data)) { return $data; }
        $rows = $data['results'] ?? ($data['data'] ?? array()); $items = array();
        foreach (array_slice((array) $rows, 0, $limit) as $row) {
            $name = $row['scientificName'] ?? ($row['species'] ?? 'Marine occurrence');
            $place = trim(implode(', ', array_filter(array($row['locality'] ?? '', $row['country'] ?? ''))));
            $items[] = self::record($row['id'] ?? ($row['occurrenceID'] ?? wp_generate_uuid4()), 'OBIS', 'Marine biology', $name, $place ?: 'Marine biodiversity occurrence', $row['eventDate'] ?? ($row['date_mid'] ?? null), 'https://obis.org/', array('type'=>'marine_occurrence','location'=>array('longitude'=>$row['decimalLongitude'] ?? null,'latitude'=>$row['decimalLatitude'] ?? null),'taxonomy'=>array('scientificName'=>$name,'kingdom'=>$row['kingdom'] ?? null,'phylum'=>$row['phylum'] ?? null)));
        }
        return $items;
    }

    private static function pubmed($limit, $params) {
        $settings = wp_parse_args((array) get_option('sc_lab_settings', array()), SC_Lab_Admin::defaults());
        $term = sanitize_text_field(isset($params['q']) ? $params['q'] : '(biology OR chemistry OR marine biology OR materials science)');
        $base = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/';
        $common = array('db'=>'pubmed','retmode'=>'json','tool'=>$settings['ncbi_tool'],'email'=>$settings['ncbi_email']);
        $search = self::remote_json(add_query_arg(array_merge($common, array('term'=>$term,'retmax'=>$limit,'sort'=>'pub date')), $base . 'esearch.fcgi'));
        if (is_wp_error($search)) { return $search; }
        $ids = $search['esearchresult']['idlist'] ?? array(); if (!$ids) { return array(); }
        $summary = self::remote_json(add_query_arg(array_merge($common, array('id'=>implode(',', $ids))), $base . 'esummary.fcgi'));
        if (is_wp_error($summary)) { return $summary; }
        $items = array();
        foreach ($ids as $id) {
            $row = $summary['result'][$id] ?? array(); $authors = array_map(function($a){ return $a['name'] ?? ''; }, (array) ($row['authors'] ?? array()));
            $items[] = self::record($id, 'PubMed', 'Life and chemical sciences', $row['title'] ?? 'PubMed record', implode(', ', array_slice(array_filter($authors),0,4)), $row['pubdate'] ?? null, 'https://pubmed.ncbi.nlm.nih.gov/' . rawurlencode($id) . '/', array('type'=>'literature','journal'=>$row['fulljournalname'] ?? ($row['source'] ?? '')));
        }
        return $items;
    }

    private static function arxiv($limit, $params) {
        $query = sanitize_text_field(isset($params['q']) ? $params['q'] : 'all:physics OR all:astronomy OR all:materials OR all:engineering');
        $url = add_query_arg(array('search_query'=>$query,'start'=>0,'max_results'=>$limit,'sortBy'=>'submittedDate','sortOrder'=>'descending'), 'https://export.arxiv.org/api/query');
        $response = wp_safe_remote_get($url, array('timeout'=>18,'headers'=>array('User-Agent'=>'SustainableCatalystLab/0.1.0')));
        if (is_wp_error($response)) { return $response; }
        $body = wp_remote_retrieve_body($response); if (!function_exists('simplexml_load_string')) { return new WP_Error('xml_unavailable','XML parser unavailable.',array('status'=>500)); }
        $xml = simplexml_load_string($body); if (!$xml) { return new WP_Error('source_parse_error','arXiv returned invalid XML.',array('status'=>502)); }
        $items = array();
        $atom = $xml->children('http://www.w3.org/2005/Atom');
        foreach ($atom->entry as $entry) {
            $entry_atom = $entry->children('http://www.w3.org/2005/Atom');
            $id = (string) $entry_atom->id; $authors = array();
            foreach ($entry_atom->author as $author) { $authors[] = (string) $author->name; }
            $items[] = self::record(md5($id), 'arXiv', 'Physics, materials and engineering', trim((string) $entry_atom->title), implode(', ', array_slice($authors,0,4)), (string) $entry_atom->published, $id, array('type'=>'preprint','abstract'=>trim((string) $entry_atom->summary)));
        }
        return $items;
    }
}
