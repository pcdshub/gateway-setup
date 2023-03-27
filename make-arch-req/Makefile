# Gateway archive Makefile

IOC_DATA = /reg/d/iocData
MSI = /reg/g/pcds/epics/base/R3.15.5-2.0/bin/$(EPICS_HOST_ARCH)/msi

GATEWAYS += fee-gasdet

$(foreach GW, $GATEWAYS, \
	$(eval $(call PREFIX_TEMPLATE,$(GW))))

#ARCHIVE = $(subst %,$(IOC_DATA)/archive/ioc-%-gateway.archive,$(GATEWAYS))
ARCHIVE = $(patsubst %,ioc-%-gateway.archive,$(GATEWAYS))

install: $(ARCHIVE)

define PREFIX_template
$1_PREFIX = $(shell echo $(1) | tr [:lower:] [:upper:] | tr - :)
endef

$(IOC_DATA)/ioc-%-gateway/archive:
	mkdir -p $@

ioc-%-gateway.archive: $(IOC_DATA)/ioc-%-gateway/archive

ioc-%-gateway.archive: gateway.tpl-arch
	$(MSI) -V -M PREFIX= $< > $@
