#include <string>

void compute_hashes(const unsigned char* data, const unsigned long n, unsigned char* md5, unsigned char* sha1, unsigned char* sha256);
std::string to_hexstring(const char* data, const unsigned long n);
