#include <sstream>

#include <openssl/md5.h>
#include <openssl/sha.h>
#include <boost/format.hpp>

void compute_hashes(const unsigned char* data, const unsigned long n, unsigned char* md5, unsigned char* sha1, unsigned char* sha256) {
	MD5(data, n, md5);
	SHA1(data, n, sha1);
	SHA256(data, n, sha256);
}

std::string to_hexstring(const char* data, const unsigned long n) {
	std::stringstream ss;
	for (auto i=0; i<n; i++)
		ss<< boost::format("%02x") % (int)(data[i]&0xff);
	return ss.str();
}
