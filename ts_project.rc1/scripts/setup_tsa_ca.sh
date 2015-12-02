#! /bin/bash

######
# Helper functions
####
cannonical() {
    readlink -f "$*"
}

try_quiet() {
    $*
    if [ $? != 0 ]; then
        echo "..failed."
        exit $?
    fi
}

try() {
    $*
    if [ $? != 0 ]; then
        echo "..failed."
        exit $?
    fi
    echo "..success."
}


######
# Preparation
####

# No filename was specified, use current dir..
if [ ! '$1' ]; then
    echo "target is current directory."
    TARGET="$(pwd)"
else
    TARGET=$(cannonical "$1")
fi

# Invalid filename was specified..
if [ ! "$TARGET" ]; then
    echo 'Cannot use the target "'"$1"'".'
    echo 'Try a target whose parent exists.'
    exit 1
fi

echo 'This will create an openssl timestamp certificate authority in:'
echo "${TARGET}"
echo '..it is highly recommended that you use an empty directory.'
read -p 'Hit ctrl-c to cancel, or hit enter to continue'

mkdir -p "${TARGET}"

# Change dir to target if we need to
if [ "$(pwd)" != "$TARGET" ]; then
    echo "Changing directory to $TARGET"
    try_quiet cd "${TARGET}"
fi

# Escape Target using \ characters, as that is what works in the OpenSSL file
TARGET=$(printf %q "${TARGET}")


######
# OpenSSL Configuration
###

# Write the openssl.cnf file, with "$TARGET" as the CA and TSA directory.
echo "Creating openssl.cnf.."
try touch openssl.cnf

##########################################################################
cat > openssl.cnf << EOF
#
# OpenSSL example configuration file.
# This is mostly being used for generation of certificate requests.
#

# This definition stops the following lines choking if HOME isn't
# defined.
HOME			= .
RANDFILE		= \$ENV::HOME/.rnd

# Extra OBJECT IDENTIFIER info:
#oid_file		= \$ENV::HOME/.oid
oid_section		= new_oids

# To use this configuration file with the "-extfile" option of the
# "openssl x509" utility, name here the section containing the
# X.509v3 extensions to use:
# extensions		= 
# (Alternatively, use a configuration file that has only
# X.509v3 extensions in its main [= default] section.)

[ new_oids ]

# We can add new OIDs in here for use by 'ca', 'req' and 'ts'.
# Add a simple OID like this:
# testoid1=1.2.3.4
# Or use config file substitution like this:
# testoid2=\${testoid1}.5.6

# Policies used by the TSA examples.
tsa_policy1 = 1.2.3.4.1
tsa_policy2 = 1.2.3.4.5.6
tsa_policy3 = 1.2.3.4.5.7

####################################################################
[ ca ]
default_ca	= CA_default		# The default ca section

####################################################################
[ CA_default ]

dir	        = ${TARGET}		 # Where everything is kept
certs		= \$dir/certs		# Where the issued certs are kept
crl_dir		= \$dir/crl		# Where the issued crl are kept
database	= \$dir/index.txt	# database index file.
#unique_subject	= no			# Set to 'no' to allow creation of
					# several ctificates with same subject.
new_certs_dir	= \$dir/newcerts		# default place for new certs.

certificate	= \$dir/certs/ts_server_authority_cert.pem 	# The CA certificate
serial		= \$dir/serial 		# The current serial number
crlnumber	= \$dir/crlnumber	# the current crl number
					# must be commented out to leave a V1 CRL
crl		= \$dir/crl.pem 		# The current CRL
private_key	= \$dir/private/ts_server_authority.pem# The private key
RANDFILE	= \$dir/private/.rand	# private random number file

x509_extensions	= usr_cert		# The extentions to add to the cert

# Comment out the following two lines for the "traditional"
# (and highly broken) format.
name_opt 	= ca_default		# Subject Name options
cert_opt 	= ca_default		# Certificate field options

# Extension copying option: use with caution.
# copy_extensions = copy

# Extensions to add to a CRL. Note: Netscape communicator chokes on V2 CRLs
# so this is commented out by default to leave a V1 CRL.
# crlnumber must also be commented out to leave a V1 CRL.
# crl_extensions	= crl_ext

default_days	= 365			# how long to certify for
default_crl_days= 30			# how long before next CRL
default_md	= default		# use public key default MD
preserve	= no			# keep passed DN ordering

# A few difference way of specifying how similar the request should look
# For type CA, the listed attributes must be the same, and the optional
# and supplied fields are just that :-)
policy		= policy_match

# For the CA policy
[ policy_match ]
countryName		= match
stateOrProvinceName	= match
organizationName	= match
organizationalUnitName	= optional
commonName		= supplied
emailAddress		= optional

# For the 'anything' policy
# At this point in time, you must list all acceptable 'object'
# types.
[ policy_anything ]
countryName		= optional
stateOrProvinceName	= optional
localityName		= optional
organizationName	= optional
organizationalUnitName	= optional
commonName		= supplied
emailAddress		= optional

####################################################################
[ req ]
default_bits		= 2048
default_keyfile 	= privkey.pem
distinguished_name	= req_distinguished_name
attributes		= req_attributes
x509_extensions	= v3_ca	# The extentions to add to the self signed cert

# Passwords for private keys if not present they will be prompted for
# input_password = secret
# output_password = secret

# This sets a mask for permitted string types. There are several options. 
# default: PrintableString, T61String, BMPString.
# pkix	 : PrintableString, BMPString (PKIX recommendation before 2004)
# utf8only: only UTF8Strings (PKIX recommendation after 2004).
# nombstr : PrintableString, T61String (no BMPStrings or UTF8Strings).
# MASK:XXXX a literal mask value.
# WARNING: ancient versions of Netscape crash on BMPStrings or UTF8Strings.
string_mask = utf8only

# req_extensions = v3_req # The extensions to add to a certificate request

[ req_distinguished_name ]
countryName			= Country Name (2 letter code)
countryName_default		= AU
countryName_min			= 2
countryName_max			= 2

stateOrProvinceName		= State or Province Name (full name)
stateOrProvinceName_default	= Some-State

localityName			= Locality Name (eg, city)

0.organizationName		= Organization Name (eg, company)
0.organizationName_default	= Internet Widgits Pty Ltd

# we can do this but it is not needed normally :-)
#1.organizationName		= Second Organization Name (eg, company)
#1.organizationName_default	= World Wide Web Pty Ltd

organizationalUnitName		= Organizational Unit Name (eg, section)
#organizationalUnitName_default	=

commonName			= Common Name (e.g. server FQDN or YOUR name)
commonName_max			= 64

emailAddress			= Email Address
emailAddress_max		= 64

# SET-ex3			= SET extension number 3

[ req_attributes ]
challengePassword		= A challenge password
challengePassword_min		= 4
challengePassword_max		= 20

unstructuredName		= An optional company name

[ usr_cert ]

# These extensions are added when 'ca' signs a request.

# This goes against PKIX guidelines but some CAs do it and some software
# requires this to avoid interpreting an end user certificate as a CA.

basicConstraints=CA:FALSE

# Here are some examples of the usage of nsCertType. If it is omitted
# the certificate can be used for anything *except* object signing.

# This is OK for an SSL server.
# nsCertType			= server

# For an object signing certificate this would be used.
# nsCertType = objsign

# For normal client use this is typical
# nsCertType = client, email

# and for everything including object signing:
# nsCertType = client, email, objsign

# This is typical in keyUsage for a client certificate.
# keyUsage = nonRepudiation, digitalSignature, keyEncipherment

# This will be displayed in Netscape's comment listbox.
nsComment			= "OpenSSL Generated Certificate"

# PKIX recommendations harmless if included in all certificates.
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid,issuer

# This stuff is for subjectAltName and issuerAltname.
# Import the email address.
# subjectAltName=email:copy
# An alternative to produce certificates that aren't
# deprecated according to PKIX.
# subjectAltName=email:move

# Copy subject details
# issuerAltName=issuer:copy

#nsCaRevocationUrl		= http://www.domain.dom/ca-crl.pem
#nsBaseUrl
#nsRevocationUrl
#nsRenewalUrl
#nsCaPolicyUrl
#nsSslServerName

# This is required for TSA certificates.
extendedKeyUsage = critical,timeStamping

[ v3_req ]

# Extensions to add to a certificate request

basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment

[ v3_ca ]


# Extensions for a typical CA


# PKIX recommendation.

subjectKeyIdentifier=hash

authorityKeyIdentifier=keyid:always,issuer

# This is what PKIX recommends but some broken software chokes on critical
# extensions.
#basicConstraints = critical,CA:true
# So we do this instead.
basicConstraints = CA:true

# Key usage: this is typical for a CA certificate. However since it will
# prevent it being used as an test self-signed certificate it is best
# left out by default.
# keyUsage = cRLSign, keyCertSign

# Some might want this also
# nsCertType = sslCA, emailCA

# Include email address in subject alt name: another PKIX recommendation
# subjectAltName=email:copy
# Copy issuer details
# issuerAltName=issuer:copy

# DER hex encoding of an extension: beware experts only!
# obj=DER:02:03
# Where 'obj' is a standard or added object
# You can even override a supported extension:
# basicConstraints= critical, DER:30:03:01:01:FF

[ crl_ext ]

# CRL extensions.
# Only issuerAltName and authorityKeyIdentifier make any sense in a CRL.

# issuerAltName=issuer:copy
authorityKeyIdentifier=keyid:always

[ proxy_cert_ext ]
# These extensions should be added when creating a proxy certificate

# This goes against PKIX guidelines but some CAs do it and some software
# requires this to avoid interpreting an end user certificate as a CA.

basicConstraints=CA:FALSE

# Here are some examples of the usage of nsCertType. If it is omitted
# the certificate can be used for anything *except* object signing.

# This is OK for an SSL server.
# nsCertType			= server

# For an object signing certificate this would be used.
# nsCertType = objsign

# For normal client use this is typical
# nsCertType = client, email

# and for everything including object signing:
# nsCertType = client, email, objsign

# This is typical in keyUsage for a client certificate.
# keyUsage = nonRepudiation, digitalSignature, keyEncipherment

# This will be displayed in Netscape's comment listbox.
nsComment			= "OpenSSL Generated Certificate"

# PKIX recommendations harmless if included in all certificates.
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid,issuer

# This stuff is for subjectAltName and issuerAltname.
# Import the email address.
# subjectAltName=email:copy
# An alternative to produce certificates that aren't
# deprecated according to PKIX.
# subjectAltName=email:move

# Copy subject details
# issuerAltName=issuer:copy

#nsCaRevocationUrl		= http://www.domain.dom/ca-crl.pem
#nsBaseUrl
#nsRevocationUrl
#nsRenewalUrl
#nsCaPolicyUrl
#nsSslServerName

# This really needs to be in place for it to be a proxy certificate.
proxyCertInfo=critical,language:id-ppl-anyLanguage,pathlen:3,policy:foo

####################################################################
[ tsa ]

default_tsa = tsa_config1	# the default TSA section

[ tsa_config1 ]

# These are used by the TSA reply generation only.
dir		=  ${TARGET}	# TSA root directory
serial		= \$dir/tsaserial	# The current serial number (mandatory)
crypto_device	= builtin		# OpenSSL engine to use for signing
signer_cert	= \$dir/certs/ts_server_cert.pem 	# The TSA signing certificate
					# (optional)
certs		= \$dir/certs.chain	# Certificate chain to include in reply
					# (optional)
signer_key	= \$dir/private/ts_server.pem # The TSA private key (optional)

default_policy	= tsa_policy1		# Policy if request did not specify it
					# (optional)
other_policies	= tsa_policy2, tsa_policy3	# acceptable policies (optional)
# Acceptable message digests (mandatory)
digests		= md5, sha1, sha1, sha224, sha256, sha384, sha512, whirlpool
accuracy	= secs:1, millisecs:500, microsecs:100	# (optional)
clock_precision_digits  = 0	# number of digits after dot. (optional)
ordering		= yes	# Is ordering defined for timestamps?
				# (optional, default: no)
tsa_name		= yes	# Must the TSA name be included in the reply?
				# (optional, default: no)
ess_cert_id_chain	= no	# Must the ESS cert id chain be included?
				# (optional, default: no)

EOF
##########################################################################


######
# Set up Certificate Authority
####

mkdir -p private
mkdir -p certs
mkdir -p newcerts
mkdir -p certsdb
mkdir -p crl
mkdir -p certreqs
touch index.txt
echo 01 > serial

#Create the CA cert
try openssl req -config openssl.cnf -days 3650 -x509 -newkey rsa:2048 -out certs/ts_server_authority_cert.pem -outform PEM
try mv privkey.pem private/ts_server_authority.pem

# Create a Private Key for the Time Service Authority
try openssl genrsa -aes256 -out private/ts_server.pem 2048

# Generate a request for a Certificate from the CA
try openssl req -new -key private/ts_server.pem -out ts_server.csr

echo "Note: The organization should be the same as the CA due to constraints in"
echo "openssl.cnf (You can change the cnf file to override this however)"

# Generate and sign the certificate from a request signed by the CA
try openssl ca -config openssl.cnf -in ts_server.csr -out certs/ts_server_cert.pem

try cat certs/ts_server_authority_cert.pem > certs.chain

#Generate a TSA sign request
echo "foo" > test.txt
echo "Generate a TSA sign request - test.tsq"
try openssl ts -query -data test.txt -no_nonce -out test.tsq -sha256

# Generate a TSA response from a request file
echo "Generate a TSA .tsr response from request"
try openssl ts -reply -queryfile test.tsq -out test.response.tsr -config openssl.cnf

#Note: openssl.cnf has who the root CA is as well as signer and private key,
#options:
#
#-inkey ts_server.pem -signer certs/ts_server_cert.pem

#Generate the TS token (not in TS response format) from a request file
echo 'Generate the TSA .der response from request (token)'
try openssl ts -reply -queryfile test.tsq -out test.response.der -token_out -config openssl.cnf

#Validate TS token
echo "Validate TS Response"
try openssl ts -verify -data test.txt -in test.response.tsr -CAfile certs/ts_server_authority_cert.pem -untrusted certs/ts_server_cert.pem
echo "Validate TS Response (token)"
try openssl ts -verify -data test.txt -in test.response.der -token_in -CAfile certs/ts_server_authority_cert.pem -untrusted certs/ts_server_cert.pem

echo All actions succeeded.
