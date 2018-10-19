#include "filemeta/hashes.h"

#include <iostream>
#include <fstream>
#include <iomanip>
#include <string>

#include <gflags/gflags.h>

static bool ValidateInput(const char* flagname, const std::string& value) {
	if (value.length() == 0) {
		std::cout<<"please provide flag '"<<flagname<<"'"<<std::endl;
		return false;
	}

	std::ifstream fs(value, std::ifstream::binary);
	if (!fs) {
		std::cout<<"file '"<<value<<"' cannot be opened"<<std::endl;
		return false;
	}
	else
		fs.close();

	return true;
} 

DEFINE_string(in, "", "input string");
DEFINE_validator(in, &ValidateInput);
int main(int argc, char** argv) {
	gflags::ParseCommandLineFlags(&argc, &argv, true);
	unsigned char md5[16], sha1[20], sha256[32];
	
	std::ifstream fs(FLAGS_in, std::ifstream::binary);
	fs.seekg (0, fs.end);
    int length = fs.tellg();
    fs.seekg (0, fs.beg);

	char* data = new char[length];
	fs.read(data, length);
	fs.close();

	compute_hashes(reinterpret_cast<const unsigned char*>(data), length, md5, sha1, sha256);
	delete[] data;

	auto md5string = to_hexstring(reinterpret_cast<const char*>(md5), 16);
	auto sha1string = to_hexstring(reinterpret_cast<const char*>(sha1), 20);
	auto sha256string = to_hexstring(reinterpret_cast<const char*>(sha256), 32);
	std::cout<<"input file:"<<FLAGS_in<<std::endl;
	std::cout<<"size   :"<<length<<" bytes"<<std::endl;
	std::cout<<"md5    :"<<md5string<<std::endl;
	std::cout<<"sha1   :"<<sha1string<<std::endl;
	std::cout<<"sha256 :"<<sha256string<<std::endl;

	std::ofstream ofs("result.meta");
	ofs<<"input file:"<<FLAGS_in<<std::endl;
	ofs<<"size   :"<<length<<" bytes"<<std::endl;
	ofs<<"md5    :"<<md5string<<std::endl;
	ofs<<"sha1   :"<<sha1string<<std::endl;
	ofs<<"sha256 :"<<sha256string<<std::endl;
	ofs.close();

	return 0;
}
