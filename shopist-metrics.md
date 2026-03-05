# Shopist Metrics Catalog

All custom and synthetic metrics being sent to the Datadog platform from the Shopist demo app.

---

## Shopist Custom Metrics

**Source:** `synthesizer/main.py`, `scenarios/application.py`

| Metric Name | Type | Source | Tags |
|---|---|---|---|
| `shopist.user.login_attempt.failure_count` | increment | `synthesizer/main.py` | `user_ip_address`, `user_id` |
| `shopist.user.login_attempt.success_count` | increment | `synthesizer/main.py` | `user_ip_address`, `user_id` |
| `shopist.web.up` | gauge | `synthesizer/main.py` | — |
| `shopist.synthesizer.errors` | distribution | `synthesizer/main.py` | — |
| `shopist.scenarios.checkout.failures` | gauge | `scenarios/application.py` | `env:prod` |

---

## Synthesizer Test Metrics

**Source:** `synthesizer/suite.py` — instrument shape variants (anomaly, shift, trend)

| Metric Name | Variants |
|---|---|
| `dd.synth.test.sawtooth` | `.a`, `.s`, `.t`, `.as`, `.at`, `.ts`, `.ast` |
| `dd.synth.test.regspike` | `.a`, `.s`, `.t`, `.as`, `.at`, `.ts`, `.ast` |
| `dd.synth.test.bushour` | `.a`, `.s`, `.t`, `.as`, `.at`, `.ts`, `.ast` |
| `dd.synth.live_riders` | — |
| `synth.funnel.sales_completed` | — |

---

## Funnel & Application Performance Metrics

**Source:** `synthesizer/suite.py`, `scenarios/application.py`

Prefix pattern: `shopist.` or environment-specific prefix.

| Metric Name | Type |
|---|---|
| `{prefix}funnel.pct_carts_abandoned` | gauge |
| `{prefix}funnel.avg_time_to_checkout` | gauge |
| `{prefix}memcache.get_hits_rate` | gauge |
| `{prefix}memcache.get_misses_rate` | gauge |
| `{prefix}memcache.curr_items` | gauge |
| `{prefix}memcache.cmd_set_rate` | gauge |
| `{prefix}memcache.bytes_written_rate` | gauge |
| `{prefix}trace.rack.request.errors` | gauge |
| `{prefix}trace.rack.request.latency.50p` | gauge |
| `{prefix}trace.mongo.query.latency.50p` | gauge |
| `{prefix}trace.mongo.query.hits` | gauge |

### Duration Percentiles (via `submit_metric_duration`)

Generated for `trace.rack.request.duration` and `trace.mongo.cmd.duration`:

| Suffix | Description |
|---|---|
| *(base)* | avg of p95+p99 |
| `.by.service.50p` | 50th percentile |
| `.by.service.75p` | 75th percentile |
| `.by.service.90p` | 90th percentile |
| `.by.service.95p` | 95th percentile |
| `.by.service.99p` | 99th percentile |
| `.by.service.100p` | max |

---

## MongoDB Metrics

**Source:** `synthesizer/suite.py`, `scenarios/application.py`

| Metric Name | Tags |
|---|---|
| `mongodb.opcounters.queryps` | `env:prod`, `cluster-name` |
| `mongodb.globallock.activeclients.readers` | `env:prod`, `cluster-name` |
| `mongodb.metrics.cursor.open.total` | `env:prod`, `cluster-name` |
| `mongodb.globallock.currentqueue.readers` | `env:prod`, `cluster-name` |
| `mongodb.mem.virtual` | `env:prod`, `cluster-name` |
| `mongodb.connections.current` | `env:prod`, `cluster-name` |
| `{prefix}mongodb.opcounters.queryps` | synth |
| `{prefix}mongodb.usage.total.countps` | synth |
| `{prefix}mongodb.usage.getmore.countps` | synth |
| `{prefix}mongodb.usage.queries.time` | synth |
| `{prefix}mongodb.network.bytesoutps` | synth |

### MongoDB Collection Size Metrics

**Source:** `python-load-generator/mongodb_utils.py`

| Metric Name | Type |
|---|---|
| `mongo.collections.cart_items.size` | gauge |
| `mongo.collections.products.size` | gauge |
| `mongo.collections.merchants.size` | gauge |
| `mongo.collections.customers.size` | gauge |
| `mongo.collections.carts.size` | gauge |
| `mongo.collections.checkouts.size` | gauge |

---

## IoT Device Metrics

**Source:** `synthesizer/main.py` (statsd), `synthesizer/suite.py` (synth instruments)

Tags: `type:iot`, `availability-zone`, `host`

### Agent

| Metric Name | Type |
|---|---|
| `datadog.agent.running` | gauge |
| `datadog.agent.started` | gauge |
| `datadog.agent.python.version` | gauge |

### System — CPU

| Metric Name | Type |
|---|---|
| `system.cpu.user` | gauge |
| `system.cpu.system` | gauge |
| `system.cpu.idle` | gauge |
| `system.cpu.iowait` | gauge |
| `system.load.1` | gauge |

### System — Disk

| Metric Name | Type |
|---|---|
| `system.disk.total` | gauge |
| `system.disk.free` | gauge |
| `system.disk.in_use` | gauge |
| `system.io.await` | gauge |

### System — Memory

| Metric Name | Type |
|---|---|
| `system.mem.total` | gauge |
| `system.mem.usable` | gauge |
| `system.swap.free` | gauge |
| `system.swap.used` | gauge |

### System — Network

| Metric Name | Type |
|---|---|
| `system.net.bytes_rcvd` | gauge |
| `system.net.bytes_sent` | gauge |

### IoT Custom Sensors (synthesizer/suite.py)

| Metric Name | Type |
|---|---|
| `device.target_temperature` | gauge |
| `device.actual_temperature` | gauge |
| `device.cpu_temperature` | gauge |
| `device.flow_rate` | gauge |
| `device.wlan_signal_dbm` | gauge |
| `device.tank_pressure` | gauge |
| `device.tank_temperature` | gauge |
| `device.product_sales` | gauge |

---

## Azure IoT Hub Metrics

**Source:** `synthesizer/main.py` (api.Metric.send), `synthesizer/suite.py`

| Metric Name |
|---|
| `azure.devices_iothubs.devices.connected_devices.all_protocol` |
| `azure.devices_iothubs.devices.total_devices` |
| `azure.devices_iothubs.d2c.twin.read.failure` |
| `azure.devices_iothubs.d2c.twin.read.success` |
| `azure.devices_iothubs.d2c.twin.update.failure` |
| `azure.devices_iothubs.d2c.twin.update.success` |
| `azure.devices_iothubs.d2c.twin.queries.failure` |
| `azure.devices_iothubs.d2c.twin.queries.success` |
| `azure.devices_iothubs.c2d.twin.read.failure` |
| `azure.devices_iothubs.c2d.twin.read.success` |
| `azure.devices_iothubs.c2d.twin.update.failure` |
| `azure.devices_iothubs.c2d.twin.update.success` |
| `azure.devices_iothubs.d2c.telemetry.egress.dropped` |
| `azure.devices_iothubs.d2c.telemetry.egress.fallback` |
| `azure.devices_iothubs.d2c.telemetry.egress.invalid` |
| `azure.devices_iothubs.d2c.telemetry.egress.success` |
| `azure.devices_iothubs.d2c.telemetry.egress.orphaned` |
| `azure.devices_iothubs.d2c.telemetry.ingress.success` |
| `azure.devices_iothubs.d2c.telemetry.ingress.all_protocol` |
| `azure.devices_iothubs.c2d.commands.egress.complete.success` |
| `azure.devices_iothubs.c2d.commands.egress.reject.success` |
| `azure.devices_iothubs.c2d.commands.egress.abandon.success` |

---

## Azure DevOps Metrics

**Source:** `synthesizer/suite.py`

| Metric Name | Type |
|---|---|
| `azure.devops.event.count` | gauge |
| `azure.devops.work_item.duration` | gauge |
| `azure.devops.build.duration` | gauge |

---

## AWS EC2 Metrics (synthesized)

**Source:** `synthesizer/suite.py`

| Metric Name |
|---|
| `{prefix}aws.ec2.status_check_failed_system` |
| `{prefix}aws.ec2.status_check_failed_instance` |
| `{prefix}aws.ec2.cpuutilization` |
| `{prefix}aws.ec2.network_out` |

---

## AWS IoT Metrics (synthesized)

**Source:** `synthesizer/suite.py`

| Metric Name |
|---|
| `aws.iot.connect_success` |
| `aws.iot.connect_auth_error` |
| `aws.iot.connect_client_error` |
| `aws.iot.connect_server_error` |
| `aws.iot.subscribe_success` |
| `aws.iot.subscribe_auth_error` |
| `aws.iot.subscribe_client_error` |
| `aws.iot.subscribe_server_error` |
| `aws.iot.subscribe_throttle` |
| `aws.iot.publishin_success` |
| `aws.iot.publishin_auth_error` |
| `aws.iot.publishin_client_error` |
| `aws.iot.publishin_server_error` |
| `aws.iot.publishin_throttle` |
| `aws.iot.publishout_success` |
| `aws.iot.publishout_auth_error` |
| `aws.iot.publishout_client_error` |
| `aws.iot.publishout_server_error` |
| `aws.iot.publishout_throttle` |
| `aws.iot.updatethingshadow_accepted` |
| `aws.iot.getthingshadow_accepted` |
| `aws.iot.deletethingshadow_accepted` |

---

## SNMP Metrics (synthesized)

**Source:** `synthesizer/suite.py`

| Metric Name |
|---|
| `snmp.udpHCInDatagrams` |
| `snmp.udpHCOutDatagrams` |
| `snmp.tcpHCInSegs` |
| `snmp.tcpHCOutSegs` |
| `snmp.tcpActiveOpens` |
| `snmp.tcpEstabResets` |
| `snmp.ifHCInOctets.rate` |
| `snmp.ifHCOutOctets.rate` |
| `snmp.ifHighSpeed` |
| `snmp.ifHCInBroadcastPkts` |
| `snmp.ifHCOutMulticastPkts` |
| `snmp.ifHCInOctets` |
| `snmp.ifHCOutOctets` |

---

## Cloud Foundry Metrics (synthesized)

**Source:** `synthesizer/main.py` — Tags: `deployment:cf-272bc51462f5eda69492`

| Metric Name |
|---|
| `cloudfoundry.nozzle.cc.job_queue_length.total` |
| `cloudfoundry.nozzle.DopplerServer.TruncatingBuffer.totalDroppedMessages` |
| `cloudfoundry.nozzle.etcd.Watchers` |
| `cloudfoundry.nozzle.slowConsumerAlert` |
| `cloudfoundry.nozzle.RequestLatency` |
| `cloudfoundry.nozzle.AuctioneerFetchStatesDuration` |
| `cloudfoundry.nozzle.UnhealthyCell` |
| `cloudfoundry.nozzle.AuctioneerLRPAuctionsFailed` |
| `cloudfoundry.nozzle.AuctioneerLRPAuctionsStarted` |
| `cloudfoundry.nozzle.rep.CapacityRemainingMemory` |

---

## Load Generator Metrics

**Source:** `python-load-generator/`

| Metric Name | Source File |
|---|---|
| `load_generator.common.request.empty` | `common.py` |
| `load_generator.common.request.attempt` | `common.py` |
| `load_generator.common.request.failed.connect` | `common.py` |
| `load_generator.common.request.sleep.connect` | `common.py` |
| `load_generator.common.request.failed.other` | `common.py` |
| `load_generator.common.request.sleep.other` | `common.py` |
| `load_generator.common.request.skipped` | `common.py` |
| `load_generator.startup.error` | `rails_generator.py` |
| `appsec_generator.db.failed` | `appsec/utilities.py` |
| `appsec_generator.trace.reqs` | `appsec/model.py` |
| `appsec_generator.trace.successful` | `appsec/model.py` |
| `appsec_generator.trace.failed` | `appsec/model.py` |
| `appsec_generator.signal.trigger` | `appsec/scenarios.py` |
| `appsec_generator.signal.trigger.failed` | `appsec/scenarios.py` |
| `appsec_generator.signal.trigger.successful` | `appsec/scenarios.py` |
| `dd_trace_demo.load_generator.cassandra_table.hits` | `bad_cassandra_cleaner_old.py` |
| `dd_trace_demo.load_generator.cassandra_table.errors` | `bad_cassandra_cleaner_old.py` |
| `dd_trace_demo.load_generator.cassandra_cleaner.hits` | `bad_cassandra_cleaner_old.py` |
| `dd_trace_demo.load_generator.cassandra_cleaner.errors` | `bad_cassandra_cleaner_old.py` |

---

## DSM / Data Streams Metrics

**Source:** `dsm-services-py/dsm_services_py/dlq_emitter.py`

| Metric Name |
|---|
| `data_streams.sqs.dead_letter_queue.messages` |
| `data_streams.sqs.dead_letter_queue.test` |
