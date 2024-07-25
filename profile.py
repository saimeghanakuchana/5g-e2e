import geni.portal as portal
import geni.rspec.pg as pg
import geni.rspec.igext as ig
import geni.rspec.emulab.pnext as PN


tour_description = """
Deploy a single network-based SDR.
"""

tour_instructions = """
"""

UBUNTU_IMG = "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU22-64-STD"
COMP_MANAGER_ID = "urn:publicid:IDN+emulab.net+authority+cm"

pc = portal.Context()

node_types = [
    ("d430", "Emulab, d430"),
    ("d740", "Emulab, d740"),
    ("d840", "Emulab, d840"),
]
pc.defineParameter(
    name="compute_node_type",
    description="Type of compute node to pair with X310 SDR",
    typ=portal.ParameterType.STRING,
    defaultValue=node_types[0],
    legalValues=node_types
)

pc.defineParameter(
    name="compute_node_image",
    description="Disk image to load on the compute node",
    typ=portal.ParameterType.STRING,
    defaultValue=UBUNTU_IMG
)

pc.defineParameter(
    name="compute_node_id",
    description="ID of the compute node to pair with SDR",
    typ=portal.ParameterType.STRING,
    defaultValue=""
)

pc.defineParameter(
    name="sdr_node_id",
    description="ID of the SDR",
    typ=portal.ParameterType.STRING,
    defaultValue=""
)

pc.defineParameter(
    name="sdr_host_address",
    description="IP address to use on the SDR host",
    typ=portal.ParameterType.STRING,
    defaultValue="192.168.40.1"
)

params = pc.bindParameters()
pc.verifyParameters()
request = pc.makeRequestRSpec()

node = request.RawPC("host")
node.component_manager_id = COMP_MANAGER_ID
if params.compute_node_id:
    node.component_id = params.compute_node_id
else:
    node.hardware_type = params.compute_node_type

node.disk_image = params.compute_node_image
node_sdr_if = node.addInterface("sdr-if")
node_sdr_if.addAddress(pg.IPv4Address(params.sdr_host_address, "255.255.255.0"))
node.addService(pg.Execute(shell="bash", command="/local/repository/bin/tune-sdr-iface.sh"))
node.startVNC()

sdr = request.RawPC(params.sdr_node_id)
sdr.component_id = params.sdr_node_id
sdr.component_manager_id = COMP_MANAGER_ID

sdr_link = request.Link("sdr-link")
sdr_link.addInterface(node_sdr_if)
sdr_link.addNode(sdr)

tour = ig.Tour()
tour.Description(ig.Tour.MARKDOWN, tour_description)
tour.Instructions(ig.Tour.MARKDOWN, tour_instructions)
request.addTour(tour)

pc.printRequestRSpec(request)
