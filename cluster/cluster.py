import json
from jinja2 import Template

# jsonString = """
# {
#   "cluster_id": "someclusterid-1243",
#   "cluster_name": "my-cluster",
#   "spark_version": "5.3.x-scala2.11",
#   "node_type_id": "i3.xlarge",
#   "autoscale": {
#         "min_workers": 2,
#         "max_workers": 8
#   }
# }
# """

jsonString = """
{
         "cluster_id":"0318-151752-abed99",
         "driver":{
            "public_dns":"",
            "node_id":"cd18c7bcd6ce41e9abfe1ea0b43590d6",
            "node_aws_attributes":{
               "is_spot":false
            },
            "instance_id":"i-00eb95eb6a35341ce",
            "start_timestamp":1592815837080,
            "host_private_ip":"10.0.233.145",
            "private_ip":"10.0.250.243"
         },
         "executors":[
            {
               "public_dns":"",
               "node_id":"5d024284dd93442aae5c41e3ec355c5b",
               "node_aws_attributes":{
                  "is_spot":false
               },
               "instance_id":"i-0ebef673cfb4b2efc",
               "start_timestamp":1592982646556,
               "host_private_ip":"10.0.252.39",
               "private_ip":"10.0.243.187"
            }
         ],
         "spark_context_id":1277495234349718182,
         "jdbc_port":10000,
         "cluster_name":"Shared Autoscaling",
         "spark_version":"6.6.x-cpu-ml-scala2.11",
         "spark_conf":{
            "spark.databricks.conda.condaMagic.enabled":"true"
         },
         "aws_attributes":{
            "zone_id":"us-west-2c",
            "first_on_demand":1,
            "availability":"SPOT_WITH_FALLBACK",
            "instance_profile_arn":"arn:aws:iam::997819012307:instance-profile/shard-demo-s3-access",
            "spot_bid_price_percent":100,
            "ebs_volume_count":0
         },
         "node_type_id":"i3.2xlarge",
         "driver_node_type_id":"i3.4xlarge",
         "custom_tags":{
            "KeepAlive":"True"
         },
         "autotermination_minutes":240,
         "enable_elastic_disk":true,
         "cluster_source":"UI",
         "init_scripts":[
            {
               "dbfs":{
                  "destination":"dbfs:/databricks/init_scripts/overwatch_proto.sh"
               }
            },
            {
               "dbfs":{
                  "destination":"dbfs:/databricks/jupyter/kernel_gateway_init.sh"
               }
            }
         ],
         "enable_local_disk_encryption":false,
         "state":"RUNNING",
         "state_message":"",
         "start_time":1592371009193,
         "terminated_time":0,
         "last_state_loss_time":1592887081313,
         "last_activity_time":1592887055636,
         "autoscale":{
            "min_workers":1,
            "max_workers":14
         },
         "cluster_memory_mb":187392,
         "cluster_cores":24.0,
         "default_tags":{
            "Vendor":"Databricks",
            "Creator":"mwc@databricks.com",
            "ClusterName":"Shared Autoscaling",
            "ClusterId":"0318-151752-abed99"
         },
         "creator_user_name":"mwc@databricks.com",
         "pinned_by_user_name":"100095",
         "init_scripts_safe_mode":false
      }
"""
# Left hand side is the cluster json resp
# Right hand side is the cluster terraform argument keys
# clusterResponseKeyToTFKeyMapping = {
#     "cluster_name": "cluster_name",
#     "spark_version": "spark_version",
#     "node_type_identity": "node_type_id",
#     "num_workers": "r_num_workers"
# }
cluster_resource_blocks = {
    "autoscale": """
    autoscale {
             min_workers = {{min_workers}}
             max_workers = {{max_workers}}
             
        }
    """,
    "flat_map": """
    {{property_name}} ={
        {%- for key, value in attributes.items() %}
        "{{ key }}" = "{{ value }}"
        {%- endfor %}
    }
    """,
    "flat_block": """
    {{property_name}} {
        {%- for key, value in attributes.items() %}
        {{ key }} = "{{ value }}"
        {%- endfor %}
    }
    """,
    "init_scripts": """
    {% for script in init_scripts -%}
    init_scripts {
            {% if script.dbfs %}dbfs {
                destination = "{{ script.dbfs.destination }}"
            }{%- endif %}
            {% if script.s3 %}s3 ={
            destination = "{{ script.s3.destination }}"
            {% if script.s3.region %}region = "{{ script.s3.region }}"{%- endif -%}
            {% if script.s3.endpoint %}endpoint = "{{ script.s3.endpoint }}"{%- endif -%}
            {% if script.s3.enable_encryption %}enable_encryption = "{{ script.s3.enable_encryption }}"{%- endif -%}
            {% if script.s3.encryption_type %}encryption_type = "{{ script.s3.encryption_type }}"{%- endif -%}
            {% if script.s3.kms_key %}kms_key = "{{ script.s3.kms_key }}"{%- endif -%}
            {% if script.s3.canned_acl %}canned_acl = "{{ script.s3.canned_acl }}"{%- endif -%}
           }{%- endif %}
    }
    {% endfor %}
    """,
    "custom_tags": """
    """
}
template_string = """
provider "databricks" { 
}

resource "{{ resource_name }}" "{{ resource_name }}_{{ resource_id }}" {
    {%- for key, value in attribute_map.items() %}
    {% if value == True or value == False %}{{ key }} = {{ value|lower }}{% else %}{{ key }} = "{{ value }}"{% endif -%}
    {% endfor -%}
    {%- for block in blocks -%}
    {{ block }}
    {%- endfor %}
}
"""

class ClusterSparkEnvVars:
    def __init__(self, attribute_map, blocks):
        self.attribute_map = attribute_map
        self.blocks = blocks
        self.template = Template(cluster_resource_blocks["flat_map"])


    @staticmethod
    def parse(input_dictionary):
        return ClusterCustomTags(input_dictionary, None)

    def render(self):
        return self.template.render(property_name="spark_env_vars",attributes=self.attribute_map)


class ClusterCustomTags:
    def __init__(self, attribute_map, blocks):
        self.attribute_map = attribute_map
        self.blocks = blocks
        self.template = Template(cluster_resource_blocks["flat_map"])


    @staticmethod
    def parse(input_dictionary):
        return ClusterCustomTags(input_dictionary, None)

    def render(self):
        return self.template.render(property_name="custom_tags",attributes=self.attribute_map)


class ClusterSparkConf:
    def __init__(self, attribute_map, blocks):
        self.attribute_map = attribute_map
        self.blocks = blocks
        self.template = Template(cluster_resource_blocks["flat_map"])


    @staticmethod
    def parse(input_dictionary):
        return ClusterSparkConf(input_dictionary, None)

    def render(self):
        return self.template.render(property_name="spark_conf",attributes=self.attribute_map)


class ClusterAWSAttributes:
    def __init__(self, attribute_map, blocks):
        self.attribute_map = attribute_map
        self.template = Template(cluster_resource_blocks["flat_block"])
        assert "zone_id" in attribute_map
        assert "availability" in attribute_map
        self.blocks = blocks

    @staticmethod
    def parse(input_dictionary):
        return ClusterAWSAttributes(input_dictionary, None)

    def render(self):
        return self.template.render(property_name="aws_attributes",attributes=self.attribute_map)

class ClusterInitScript:
    def __init__(self, attribute_map, blocks):
        self.attribute_map = attribute_map
        self.template = Template(cluster_resource_blocks["init_scripts"])
        for item in attribute_map:
            assert (("dbfs" in item) or ("s3" in item))
        self.blocks = blocks

    @staticmethod
    def parse(input_array):
        return ClusterInitScript(input_array, None)

    def render(self):
        return self.template.render(init_scripts=self.attribute_map)


class ClusterAutoScaleBlock:
    def __init__(self, attribute_map, blocks):
        self.attribute_map = attribute_map
        self.template = Template(cluster_resource_blocks["autoscale"])
        assert "min_workers" in attribute_map
        assert "max_workers" in attribute_map
        self.blocks = blocks

    @staticmethod
    def parse(input_dictionary):
        return ClusterAutoScaleBlock(input_dictionary, None)

    def render(self):
        return self.template.render(min_workers=self.attribute_map["min_workers"], max_workers=self.attribute_map["max_workers"])

class ClusterTFResource:
    block_key_map = {
        "autoscale": ClusterAutoScaleBlock,
        "aws_attributes": ClusterAWSAttributes,
        "spark_conf": ClusterSparkConf,
        "init_scripts": ClusterInitScript,
        "custom_tags": ClusterCustomTags,
        "spark_env_vars": ClusterSparkEnvVars
    }
    ignore_block_key = {
        "driver", "executors", "default_tags"
    }
    ignore_attribute_key = {
        "spark_context_id", "jdbc_port", "cluster_source","state", "state_message", "start_time","terminated_time",
        "last_state_loss_time","last_activity_time","cluster_memory_mb","cluster_cores","creator_user_name",
        "pinned_by_user_name","init_scripts_safe_mode","enable_local_disk_encryption","cluster_id"
    }

    def __init__(self, id, attribute_map, blocks):
        self.id = id
        self.template = Template(template_string)
        self.attribute_map = attribute_map
        self.blocks = blocks

    def render(self):
        return self.template.render(resource_name="databricks_cluster", resource_id=self.id,
                                    attribute_map=self.attribute_map,
                                    blocks=[block.render() for block in self.blocks])
class Cluster:

    def __init__(self, cluster_json):
        self.cluster_id = ""
        self.cluster_resource = {}
        self.cluster_blocks = []
        self.parse(cluster_json)

    def parse(self, cluster_json):
        for key in cluster_json.keys():
            print(key)
            # Catch all blocks
            if key in ClusterTFResource.block_key_map:
                # clusterResp[key] is the value in the json and the block_key map will point to the class to handle the block
                self.cluster_blocks += [ClusterTFResource.block_key_map[key].parse(cluster_json[key])]
            elif key not in ClusterTFResource.ignore_block_key and key not in ClusterTFResource.ignore_attribute_key:
                assert type(cluster_json[key]) is not dict
                self.cluster_resource[key] = cluster_json[key]


def test():
    clusterResp = json.loads(jsonString)
    cluster = Cluster(clusterResp)

    output_cluster = ClusterTFResource(clusterResp["cluster_id"], cluster.cluster_resource, cluster.cluster_blocks)
    print(output_cluster.render())
