
package proxies

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
	"net/url"
	"strconv"
	"strings"
)

func ProxiesToV2RayLinks(proxies []map[string]any) []string {
	links := make([]string, 0, len(proxies))
	for _, p := range proxies {
		if link := ProxyToV2RayLink(p); link != "" {
			links = append(links, link)
		}
	}
	return links
}

func ProxyToV2RayLink(p map[string]any) string {
	typ, _ := p["type"].(string)
	typ = strings.ToLower(typ)

	switch typ {
	case "vmess":
		return proxyToVmessLink(p)
	case "vless":
		return proxyToVlessLink(p)
	case "trojan":
		return proxyToTrojanLink(p)
	case "ss", "shadowsocks":
		return proxyToSSLink(p)
	case "socks5", "socks":
		return proxyToSocks5Link(p)
	case "http", "https":
		return proxyToHTTPLink(p)
	case "anytls":
		return proxyToAnyTLSLink(p)
	case "hysteria":
		return proxyToHysteriaLink(p)
	case "mieru":
		return proxyToMieruLink(p)
	default:
		return ""
	}
}

func proxyToVmessLink(p map[string]any) string {
	vmess := map[string]any{
		"v": "2",
		"ps": p["name"],
		"add": p["server"],
		"port": fmt.Sprint(p["port"]),
		"id": p["uuid"],
		"aid": fmt.Sprint(p["alterId"]),
		"scy": "auto",
		"net": p["network"],
		"type": "none",
		"host": "",
		"path": "",
		"tls": "",
		"sni": "",
		"alpn": "",
		"fp": "",
	}

	if tls, ok := p["tls"].(bool); ok && tls {
		vmess["tls"] = "tls"
	}
	if sni, ok := p["servername"].(string); ok {
		vmess["sni"] = sni
	}
	if fp, ok := p["client-fingerprint"].(string); ok {
		vmess["fp"] = fp
	}
	if alpn, ok := p["alpn"].([]any); ok && len(alpn) > 0 {
		alpnStrs := make([]string, 0, len(alpn))
		for _, a := range alpn {
			alpnStrs = append(alpnStrs, fmt.Sprint(a))
		}
		vmess["alpn"] = strings.Join(alpnStrs, ",")
	}

	if wsOpts, ok := p["ws-opts"].(map[string]any); ok {
		if path, ok := wsOpts["path"].(string); ok {
			vmess["path"] = path
		}
		if headers, ok := wsOpts["headers"].(map[string]any); ok {
			if host, ok := headers["Host"].(string); ok {
				vmess["host"] = host
			}
		}
	}

	data, _ := json.Marshal(vmess)
	b64 := base64.StdEncoding.EncodeToString(data)
	name, _ := p["name"].(string)
	return fmt.Sprintf("vmess://%s#%s", b64, url.PathEscape(name))
}

func proxyToVlessLink(p map[string]any) string {
	uuid, _ := p["uuid"].(string)
	server, _ := p["server"].(string)
	port, _ := p["port"].(int)
	name, _ := p["name"].(string)

	u := &url.URL{
		Scheme:   "vless",
		User:     url.User(uuid),
		Host:     fmt.Sprintf("%s:%d", server, port),
		Fragment: name,
	}

	query := u.Query()

	if network, ok := p["network"].(string); ok {
		query.Set("type", network)
	}

	if tls, ok := p["tls"].(bool); ok && tls {
		query.Set("security", "tls")
	}

	if sni, ok := p["servername"].(string); ok {
		query.Set("sni", sni)
		query.Set("host", sni)
	}

	if fp, ok := p["client-fingerprint"].(string); ok {
		query.Set("fp", fp)
	}

	if flow, ok := p["flow"].(string); ok {
		query.Set("flow", flow)
	}

	if wsOpts, ok := p["ws-opts"].(map[string]any); ok {
		if path, ok := wsOpts["path"].(string); ok {
			query.Set("path", path)
		}
	}

	if realityOpts, ok := p["reality-opts"].(map[string]any); ok {
		query.Set("security", "reality")
		if pk, ok := realityOpts["public-key"].(string); ok {
			query.Set("pbk", pk)
		}
		if sid, ok := realityOpts["short-id"].(string); ok {
			query.Set("sid", sid)
		}
	}

	u.RawQuery = query.Encode()
	return u.String()
}

func proxyToTrojanLink(p map[string]any) string {
	password, _ := p["password"].(string)
	server, _ := p["server"].(string)
	port, _ := p["port"].(int)
	name, _ := p["name"].(string)

	u := &url.URL{
		Scheme:   "trojan",
		User:     url.User(password),
		Host:     fmt.Sprintf("%s:%d", server, port),
		Fragment: name,
	}

	query := u.Query()
	query.Set("security", "tls")

	if sni, ok := p["servername"].(string); ok {
		query.Set("sni", sni)
	}

	if fp, ok := p["client-fingerprint"].(string); ok {
		query.Set("fp", fp)
	}

	if skipVerify, ok := p["skip-cert-verify"].(bool); ok && skipVerify {
		query.Set("allowInsecure", "1")
	}

	if wsOpts, ok := p["ws-opts"].(map[string]any); ok {
		query.Set("type", "ws")
		if path, ok := wsOpts["path"].(string); ok {
			query.Set("path", path)
		}
		if headers, ok := wsOpts["headers"].(map[string]any); ok {
			if host, ok := headers["Host"].(string); ok {
				query.Set("host", host)
			}
		}
	}

	u.RawQuery = query.Encode()
	return u.String()
}

func proxyToSSLink(p map[string]any) string {
	server, _ := p["server"].(string)
	port, _ := p["port"].(int)
	name, _ := p["name"].(string)
	cipher, _ := p["cipher"].(string)
	password, _ := p["password"].(string)

	auth := fmt.Sprintf("%s:%s", cipher, password)
	b64Auth := base64.URLEncoding.EncodeToString([]byte(auth))
	b64Auth = strings.TrimRight(b64Auth, "=")

	return fmt.Sprintf("ss://%s@%s:%d#%s", b64Auth, server, port, url.PathEscape(name))
}

func proxyToSocks5Link(p map[string]any) string {
	server, _ := p["server"].(string)
	port, _ := p["port"].(int)
	name, _ := p["name"].(string)

	u := &url.URL{
		Scheme:   "socks5",
		Host:     fmt.Sprintf("%s:%d", server, port),
		Fragment: name,
	}

	if username, ok := p["username"].(string); ok && username != "" {
		if password, ok := p["password"].(string); ok {
			u.User = url.UserPassword(username, password)
		} else {
			u.User = url.User(username)
		}
	}

	return u.String()
}

func proxyToHTTPLink(p map[string]any) string {
	server, _ := p["server"].(string)
	port, _ := p["port"].(int)
	name, _ := p["name"].(string)

	scheme := "http"
	if tls, ok := p["tls"].(bool); ok && tls {
		scheme = "https"
	}

	u := &url.URL{
		Scheme:   scheme,
		Host:     fmt.Sprintf("%s:%d", server, port),
		Fragment: name,
	}

	if username, ok := p["username"].(string); ok && username != "" {
		if password, ok := p["password"].(string); ok {
			u.User = url.UserPassword(username, password)
		} else {
			u.User = url.User(username)
		}
	}

	return u.String()
}

func proxyToAnyTLSLink(p map[string]any) string {
	password, _ := p["password"].(string)
	server, _ := p["server"].(string)
	port, _ := p["port"].(int)
	name, _ := p["name"].(string)

	u := &url.URL{
		Scheme:   "anytls",
		User:     url.User(password),
		Host:     fmt.Sprintf("%s:%d", server, port),
		Fragment: name,
	}

	query := u.Query()
	query.Set("security", "tls")

	if sni, ok := p["servername"].(string); ok {
		query.Set("sni", sni)
	}

	if skipVerify, ok := p["skip-cert-verify"].(bool); ok && skipVerify {
		query.Set("allowInsecure", "1")
		query.Set("insecure", "1")
	}

	if alpn, ok := p["alpn"].([]any); ok && len(alpn) > 0 {
		alpnStrs := make([]string, 0, len(alpn))
		for _, a := range alpn {
			alpnStrs = append(alpnStrs, fmt.Sprint(a))
		}
		query.Set("alpn", strings.Join(alpnStrs, ","))
	}

	if speed, ok := p["speed"].(int); ok {
		query.Set("speed", strconv.Itoa(speed))
	}

	if udp, ok := p["udp"].(bool); ok && udp {
		query.Set("udp", "1")
	}

	u.RawQuery = query.Encode()
	return u.String()
}

func proxyToHysteriaLink(p map[string]any) string {
	server, _ := p["server"].(string)
	port, _ := p["port"].(int)
	name, _ := p["name"].(string)
	authStr, _ := p["auth-str"].(string)
	up, _ := p["up"].(int)
	down, _ := p["down"].(int)

	u := &url.URL{
		Scheme:   "hysteria",
		Host:     fmt.Sprintf("%s:%d", server, port),
		Fragment: name,
	}

	if authStr != "" {
		u.User = url.User(authStr)
	}

	query := u.Query()

	if up > 0 {
		query.Set("up", strconv.Itoa(up))
	}
	if down > 0 {
		query.Set("down", strconv.Itoa(down))
	}

	if protocol, ok := p["protocol"].(string); ok {
		query.Set("protocol", protocol)
	}

	if sni, ok := p["sni"].(string); ok {
		query.Set("sni", sni)
		query.Set("peer", sni)
	}

	if skipVerify, ok := p["skip-cert-verify"].(bool); ok && skipVerify {
		query.Set("insecure", "1")
	}

	if alpn, ok := p["alpn"].([]any); ok && len(alpn) > 0 {
		alpnStrs := make([]string, 0, len(alpn))
		for _, a := range alpn {
			alpnStrs = append(alpnStrs, fmt.Sprint(a))
		}
		query.Set("alpn", strings.Join(alpnStrs, ","))
	}

	if speed, ok := p["speed"].(int); ok {
		query.Set("speed", strconv.Itoa(speed))
	}

	u.RawQuery = query.Encode()
	return u.String()
}

func proxyToMieruLink(p map[string]any) string {
	server, _ := p["server"].(string)
	name, _ := p["name"].(string)
	username, _ := p["username"].(string)
	password, _ := p["password"].(string)
	transport, _ := p["transport"].(string)
	multiplexing, _ := p["multiplexing"].(string)

	u := &url.URL{
		Scheme:   "mieru",
		Host:     server,
		Fragment: name,
	}

	if username != "" {
		if password != "" {
			u.User = url.UserPassword(username, password)
		} else {
			u.User = url.User(username)
		}
	}

	query := u.Query()

	if port, ok := p["port"].(int); ok {
		query.Set("port", strconv.Itoa(port))
	}

	if portRange, ok := p["port-range"].(string); ok {
		query.Set("port-range", portRange)
	}

	if transport != "" {
		query.Set("protocol", strings.ToLower(transport))
	}

	if multiplexing != "" {
		query.Set("multiplexing", strings.ToLower(multiplexing))
	}

	if speed, ok := p["speed"].(int); ok {
		query.Set("speed", strconv.Itoa(speed))
	}

	u.RawQuery = query.Encode()
	return u.String()
}
