=============================================
2	Test Plan for VMware DVS plugin version 1.1.0
3	=============================================
4
5	.. contents:: Table of contents
6	   :depth: 3
7
8	************
9	Introduction
10	************
11
12	Purpose
13	=======
14
15	Main purpose of this document is intended to describe Quality Assurance
16	activities, required to insure that  Fuel plugin for Neutron ML2  vmware_dvs
17	driver is  ready for production. The project will be able to offer VMware DVS
18	integration functionality with MOS.
19
20	The scope of this plan defines the following objectives:
21
22	* Identify testing activities;
23	* Outline testing approach, test types, test cycle that will be used;
24	* List of metrics and deliverable elements;
25	* List of items for testing and out of testing scope;
26	* Detect exit criteria in testing purposes;
27	* Describe test environment.
28
29	Scope
30	=====
31
32	Fuel VMware DVS plugin includes Neutron ML2 Driver For VMWare vCenter DVS
33	which is developed by third party. This test plan covers a full functionality
34	of Fuel VMware DVS plugin, include basic scenarios related with DVS driver for
35	Neutron.
36
37	Following test types should be provided:
38
39	* Smoke/BVT tests
40	* Integration tests
41	* System tests
42	* Destructive tests
43	* GUI tests
44
45	Performance testing will be executed on the scale lab and a custom set of
46	rally scenarios must be run with DVS environment. Configuration, enviroment
47	and scenarios for performance/scale testing should be determine separately.
48
49	Intended Audience
50	=================
51
52	This document is intended for project team staff (QA and Dev engineers and
53	managers) and all other persons who are interested in testing results.
54
55	Limitation
56	==========
57
58	Plugin (or its components) has the following limitations:
59
60	* VMware DVS plugin be enabled only in environments with Neutron as the networking option.
61	* Only VLANs are supported for tenant network separation.
62	* Only vSphere 5.5 & 6.0 are supported.
63
64	Product compatibility matrix
65	============================
66
67	.. list-table:: product compatibility matrix
68	   :widths: 15 10 30
69	   :header-rows: 1
70
71	   * - Requirement
72	     - Version
73	     - Comment
74	   * - MOS
75	     - 7.0 with Kilo
76	     -
77	   * - Operating System
78	     - Ubuntu 14.0.4
79	     -
80	   * - vSphere
81	     - 5.5, 6.0
82	     -
83
84	Test environment, infrastructure and tools
85	==========================================
86
87	Following configuration should be used in the testing:
88
89	* 1 physnet to 1 DVS switch (dvSwitch).
90
91	Other recommendation you can see in the test cases.
92
93	**************************************
94	Evaluation Mission and Test Motivation
95	**************************************
96
97	Project main goal is to build a MOS plugin that integrates a Neutron ML2
98	Driver For VMWare vCenter DVS. This will allow to use Neutron for networking
99	in vmware-related environments. The plugin must be compatible with the version
100	7.0 of Mirantis OpenStack and should be tested with sofware/hardware described
101	in `product compatibility matrix`_.
102
103	See the VMware DVS Plugin specification for more details.
104
105	Evaluation mission
106	==================
107
108	* Find important problems with integration of Neutron ML2 driver for DVS.
109	* Verify a specification.
110	* Provide tests for maintenance update.
111	* Lab environment deployment.
112	* Deploy MOS with developed plugin installed.
113	* Create and run specific tests for plugin/deployment.
114	* Verify a documentation.
115
116	*****************
117	Target Test Items
118	*****************
119
120	* Install/uninstall Fuel Vmware-DVS plugin
121	* Deploy Cluster with Fuel Vmware-DVS plugin by Fuel
122	    * Roles of nodes
123	        * controller
124	        * compute
125	        * cinder
126	        * mongo
127	        * compute-vmware
128	        * cinder-vmware
129	    * Hypervisors:
130	        * KVM+Vcenter
131	        * Qemu+Vcenter
132	    * Storage:
133	        * Ceph
134	        * Cinder
135	        * VMWare vCenter/ESXi datastore for images
136	    * Network
137	        * Neutron with Vlan segmentation
138	        * HA + Neutron with VLAN
139	    * Additional components
140	        * Ceilometer
141	        * Health Check
142	    * Upgrade master node
143	* MOS and VMware-DVS plugin
144	    * Computes(Nova)
145	        * Launch and manage instances
146	        * Launch instances in batch
147	    * Networks (Neutron)
148	        * Create and manage public and private networks.
149	        * Create and manage routers.
150	        * Port binding / disabling
151	        * Port security
152	        * Security groups
153	        * Assign vNIC to a VM
154	        * Connection between instances
155	    * Heat
156	        * Create stack from template
157	        * Delete stack
158	    * Keystone
159	        * Create and manage roles
160	    * Horizon
161	        * Create and manage projects
162	        * Create and manage users
163	    * Glance
164	        * Create  and manage images
165	* GUI
166	    * Fuel UI
167	* CLI
168	    * Fuel CLI
169
170	*************
171	Test approach
172	*************
173
174	The project test approach consists of Smoke,  Integration, System, Regression
175	Failover and Acceptance  test levels.
176
177	**Smoke testing**
178
179	The goal of smoke testing is to ensure that the most critical features of Fuel
180	VMware DVS plugin work  after new build delivery. Smoke tests will be used by
181	QA to accept software builds from Development team.
182
183	**Integration and System testing**
184
185	The goal of integration and system testing is to ensure that new or modified
186	components of Fuel and MOS work effectively with Fuel VMware DVS plugin
187	without gaps in dataflow.
188
189	**Regression testing**
190
191	The goal of regression testing is to verify that key features of  Fuel VMware
192	DVS plugin  are not affected by any changes performed during preparation to
193	release (includes defects fixing, new features introduction and possible
194	updates).
195
196	**Failover testing**
197
198	Failover and recovery testing ensures that the target-of-test can successfully
199	failover and recover from a variety of hardware, software, or network
200	malfunctions with undue loss of data or data integrity.
201
202	**Acceptance testing**
203
204	The goal of acceptance testing is to ensure that Fuel VMware DVS plugin has
205	reached a level of stability that meets requirements  and acceptance criteria.
206
207
208	***********************
209	Entry and exit criteria
210	***********************
211
212	Criteria for test process starting
213	==================================
214
215	Before test process can be started it is needed to make some preparation
216	actions - to execute important preconditions. The following steps must be
217	executed successfully for starting test phase:
218
219	* all project requirements are reviewed and confirmed;
220	* implementation of testing features has finished (a new build is ready for testing);
221	* implementation code is stored in GIT;
222	* test environment is prepared with correct configuration, installed all needed software, hardware;
223	* test environment contains the last delivered build for testing;
224	* test plan is ready and confirmed internally;
225	* implementation of manual tests and autotests (if any) has finished.
226
227	Feature exit criteria
228	=====================
229
230	Testing of a feature can be finished when:
231
232	* All planned tests (prepared before) for the feature are executed; no defects are found during this run;
233	* All planned tests for the feature are executed; defects found during this run are verified or confirmed to be acceptable (known issues);
234	* The time for testing of that feature according to the project plan has run out and Project Manager confirms that no changes to the schedule are possible.
235
236	Suspension and resumption criteria
237	==================================
238
239	Testing of a particular feature is suspended if there is a blocking issue
240	which prevents tests execution. Blocking issue can be one of the following:
241
242	* Testing environment for the feature is not ready
243	* Testing environment is unavailable due to failure
244	* Feature has a blocking defect, which prevents further usage of this feature and there is no workaround available
245
246	************
247	Deliverables
248	************
249
250	List of deliverables
251	====================
252
253	Project testing activities are to be resulted in the following reporting documents:
254
255	* Test plan
256	* Test report
257	* Automated test cases
258
259	Acceptance criteria
260	===================
261
262	* All acceptance criteria for user stories are met.
263	* All test cases are executed. BVT tests are passed
264	* Critical and high issues are fixed
265	* All required documents are delivered
266	* Release notes including a report on the known errors of that release
267
268	**********
269	Test cases
270	**********
271
272	.. include:: test_suite_smoke.rst
273	.. include:: test_suite_integration.rst
274	.. include:: test_suite_system.rst
275	.. include:: test_suite_destructive.rst
276	.. include:: test_suite_gui.rst