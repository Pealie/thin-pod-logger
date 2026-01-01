---
name: Thin-Pod v1.0 Gate Review
about: Mandatory gate review required before creating a v1.0 release tag
labels: [gate-review, v1.0]
assignees: []
---

# Thin-Pod v1.0 Gate Review

**This issue must be CLOSED with all items checked before a v1.0 tag is permitted.**  
Any unchecked item forces NO-GO.

---

## Review Metadata

- Review date:  
- Reviewer(s):  
- Repo(s):  
- Milestone: Thin-Pod v1.0 — Exit Criteria  
- Intended release tag:  
- PCB revision:  
- Firmware commit hash:

---

## Mandatory Checklist (all required)

### Hardware
- [ ] Final PCB revision frozen and published
- [ ] Schematics, PCB, BOM buildable without interpretation
- [ ] Mechanical mounting documented

### Power
- [ ] Sleep / active / TX currents measured
- [ ] Duty-cycle assumptions stated
- [ ] Energy budget reconciled
- [ ] Brown-out and cold-start characterised

### Sensor chain
- [ ] ADXL1005 chain verified end-to-end
- [ ] Noise floor and saturation documented
- [ ] Controlled excitation test logged

### Firmware
- [ ] Deterministic boot sequence
- [ ] All tasks bounded or watchdog-protected
- [ ] Error states enumerated with reason codes
- [ ] Clean-clone build succeeds

### UWB link
- [ ] Packet format versioned and frozen
- [ ] Loss / retry behaviour defined
- [ ] Gateway cold-start and recovery verified

### Fault detection
- [ ] Method stated clearly
- [ ] Training data provenance documented
- [ ] One fault mode convincingly demonstrated

### Reproducibility
- [ ] Bring-up checklist works on fresh bench
- [ ] No undocumented tools or steps
- [ ] First data achievable unaided

### External validation
- [ ] Public submission or review attempted
- [ ] Feedback logged
- [ ] Reviewed version tag preserved

### Scope lock
- [ ] Out-of-scope list written
- [ ] No post-lock feature additions

---

## Evidence (links only)

- Schematics / PCB:  
- BOM:  
- Power data:  
- Sensor tests:  
- Firmware build:  
- UWB data:  
- Fault demo:  
- Bring-up guide:  
- External review:

---

## Decision

☐ **GO** — v1.0 tag may be created  
☐ **NO-GO** — Blocking items listed below

-  
-  

---

## Enforcement Note

A v1.0 release **must reference this issue number**.  
If this issue is open or marked NO-GO, the v1.0 tag is invalid by definition.
