# libcet

The encryption algorithms reverse from 99sushe application.

## Install

```
pip install https://github.com/realityone/libcet/zip/master
```

## Usage

```
# encoding=utf-8

from libcet import cet

crypter = cet.CETCrypter('XXXXXXXX', 'XXXXXXXX')
ticket = cet.CETTicket(crypter)

print ticket.find_ticket_number('XX', 'XXX', 'XXX', cet_type=cet.CETTypes.CET6)
```