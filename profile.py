import geni.portal as portal
import geni.rspec.pg as pg
import geni.rspec.igext as ig
import geni.rspec.emulab.pnext as PN


tour_description = """
Deploy an e2e 5G network with Open5GS and OCUDU in flux office.

"""

tour_instructions = """

### Instructions

On `skull2`:

```
sudo /var/tmp/ocudu/build/apps/gnb/gnb -c /var/tmp/etc/ocudu/gnb_rf_n310_tdd_n78_20mhz.yml
```


"""

UBUNTU_IMG = "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU22-64-STD"
COTS_UE_IMG = "urn:publicid:IDN+emulab.net+image+PowderTeam:cots-jammy-image"
COTS_UE_IMG1 = "urn:publicid:IDN+emulab.net+image+PowderTeam:cots-jammy-image"
COMP_MANAGER_ID = "urn:publicid:IDN+emulab.net+authority+cm"

pc = portal.Context()

pc.defineParameter(
    name="deploy_o5gs_ocudu",
    description="Deploy OCUDU and dockerized Open5GS components",
    typ=portal.ParameterType.BOOLEAN,
    defaultValue=True
)

pc.defineParameter(
    name="gnb_node_image",
    description="Disk image to load on the gnb/core node (skull nuc)",
    typ=portal.ParameterType.STRING,
    defaultValue=UBUNTU_IMG
)

params = pc.bindParameters()
pc.verifyParameters()
request = pc.makeRequestRSpec()

core_gnb_node = request.RawPC("core-gnb")
core_gnb_node.component_manager_id = COMP_MANAGER_ID
core_gnb_node.disk_image = params.gnb_node_image
core_gnb_node.component_id = "skull2"
if params.deploy_o5gs_ocudu:
    core_gnb_node.addService(pg.Execute(shell="bash", command="/local/repository/bin/deploy-o5gs-ocudu.sh"))
    core_gnb_node.addService(pg.Execute(shell="bash", command="sudo ifconfig enp1s0f0 192.168.20.1"))
    core_gnb_node.addService(pg.Execute(shell="bash", command="/local/repository/bin/tune-sdr-iface.sh"))
core_gnb_node.startVNC()

ue_node = request.RawPC("ue")
ue_node.component_manager_id = COMP_MANAGER_ID
ue_node.component_id = "sm09"
ue_node.disk_image = COTS_UE_IMG
ue_node.addService(pg.Execute(shell="bash", command="/local/repository/bin/setup_cots_ue.sh"))
ue_node.startVNC()

ue_node1 = request.RawPC("ue1")
ue_node1.component_manager_id = COMP_MANAGER_ID
ue_node1.component_id = "sm08"
ue_node1.disk_image = COTS_UE_IMG1
ue_node1.addService(pg.Execute(shell="bash", command="/local/repository/bin/setup_cots_ue.sh"))
ue_node1.startVNC()

tour = ig.Tour()
tour.Description(ig.Tour.MARKDOWN, tour_description)
tour.Instructions(ig.Tour.MARKDOWN, tour_instructions)
request.addTour(tour)

pc.printRequestRSpec(request)
