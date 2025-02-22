import geni.portal as portal
import geni.rspec.pg as pg
import geni.rspec.igext as ig
import geni.rspec.emulab.pnext as PN


tour_description = """
Deploy an e2e 5G network with Open5GS and srsRAN in flux office.

"""

tour_instructions = """

### Instructions

"""

UBUNTU_IMG = "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU22-64-STD"
COTS_UE_IMG = "urn:publicid:IDN+emulab.net+image+PowderTeam:cots-jammy-image"
COMP_MANAGER_ID = "urn:publicid:IDN+emulab.net+authority+cm"

pc = portal.Context()

pc.defineParameter(
    name="deploy_o5gsrsran_patched",
    description="Deploy POWDER patched srsRAN and dockerized Open5GS components",
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
core_gnb_node.disk_image = params.skull_node_image
core_gnb_node.compute_node_id = "skull2"
core_gnb_node.addService(pg.Execute(shell="bash", command="/local/repository/bin/tune-sdr-iface.sh"))
if params.deploy_o5gsrsran_patched:
    core_gnb_node.addService(pg.Execute(shell="bash", command="/local/repository/bin/deploy-o5gsrsran-patched.sh"))
core_gnb_node.startVNC()

ue_node = request.RawPC("ue")
ue_node.component_manager_id = COMP_MANAGER_ID
ue_node.component_id = "sm09"
ue_node.disk_image = COTS_UE_IMG
ue_node.addService(pg.Execute(shell="bash", command="/local/repository/bin/setup_cots_ue.sh"))
ue_node.startVNC()

tour = ig.Tour()
tour.Description(ig.Tour.MARKDOWN, tour_description)
tour.Instructions(ig.Tour.MARKDOWN, tour_instructions)
request.addTour(tour)

pc.printRequestRSpec(request)
