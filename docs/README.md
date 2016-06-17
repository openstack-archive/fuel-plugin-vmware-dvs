# Table of Contents
1. [Overview](#id-section1)
   * [How to use](#id-section2)
   * [How to build documentation] (#id-section3)
2. [Check yourself](#id-section4)
   * [Plugin Guide checklist](#id-section5)

<div id='id-section1'/>

# Overview

If you are developing your own plugin for Fuel, you will also need to prepare the documentation set,
which includes Test Plan, Test Report and Plugin Guide.

<div id='id-section2'/>
## How to use

This repo is organized as the doc tree with 2 main folders:
- plugin guide
- testing documentation
  - Test Plan
  - Test Report

To use these doc templates, follow these steps:

1. Clone the repo:

   `git clone git@github.com:Mirantis/fuel-plugin-docs.git`
  
2. Populate the placeholders of the conf.py files (for Plugin Guide, Test Plan and Report) with plugin-specific information (e.g. document name, plugin release).

3. Populate the content of RST files which make up the document structure.

<div id='id-section3'/>

## How to build documentation

Once you're done with editing the conf.py and sample RST files, you should cd into the corresponding doc dir and
run `make latexpdf`.

For example:
```
cd plugin guide
make latexpdf
```

The PDF will be found in /build subdir.

<div id='id-section4'/>

## Check yourself

Please use the checklists below to make sure you documentation
meets the acceptance criteria.

<div id='id-section5'/>

### Plugin Guide

* The Plugin Guide contains plugin version in <fuel-plugin-name>-XX-XXX-X format.
* The **Overview** section provides information on the following:
  * high-level description of plugin functionality/use case
  * schemes (optional)
* The **Requirements** section provides information on the following:
  * target MOS release (e.g. should be 8.0 not 8.0 and/or higher)
  * required compatible proprietary Partner product version
  * required compatible proprietary hw/software (if applicable)
* The **Prerequisites** section provides information on what should be done prior to the solution installation/configuration, specifically:
  * List of required HW/SW and how to get it (where to order or how to download).
  * Compatible firmware versions (for HW) and software versions (for SW).
  * A link to official documentation and configuration guides of used HW/SH should be provided.
  * How to configure required external hardware/software (e.g. storage devices, switches and so on) so that user could use them via the the application/driver. A simple configuration would be enough.
  * If the solution can use specific HW/SW in several modes, then there should be instructions on how to properly configure the hw/software to use this very mode
* The **Limitations** should outline the issues that might limit the plugin usage. Those can be:
  * specific networking option available for the plugin (e.g. it can only use Neutron VXLAN)
  * known issues that might affect the plugin's operability (e.g. it's impossible to use non-ASCII characters)
* The **Release Notes** section should describe how this plugin version differs from the previous one.
* The **Installing the plugin** section provides commands and estimated output.
* The **Configuring the plugin** section provides the following information:
  * It's clarified which MOS environment configuration should be used (how many controller, computes, which options/services should be enabled). All links to the official Mirantis OpenStack documentation are present. It's also okay to provide screenshots.
  * It's clarified how to configure MOS environment properly for the plugin usage (e.g. how to configure interfaces for different logical networks Fuel uses). It's also okay to provide screenshots.
  * If the plugin requires specific role/naming convention, then this is also outlined.
  * UI part of the plugin should have detailed description and instructions on where to get specific params. This should be done for every field and example values should be provided.
  * If the plugin supports several modes of usage, then there should be a flow for each mode (e.g. each mode should be presented as the step-by-step instruction with screenshots with all required UI elements listed in the correct order):
e.g. Select plugin checkbox, click a radio button, fill in the text fields
 * Network verification check is specified as the obligatory step prior to deployment. If it’s expected to fail, this fact should be explicitly stated and a reason should be provided.
* The **User Guide** should contain:
  * baseline commands (CLI reference) with the estimated output (e.g. create volumes, list volumes etc)
  * links to external documentation (e.g. if all baseline issues are covered in open source/proprietary  documentation) 
* The **Verification** section should explain how to verify that the plugin works as expected (CLI, expected output).
* The **Troubleshooting** section should deliver specific guidaince on:
  * how to make sure that all services are running
  * how to check network connectivity (if needed)
  * logs (where to find those, what to pay attention to)
 




