# EduLedger ERP — Known Operational Boundaries & Technical Specifications
**Target Version**: v2.0.0 (Production Release)  

---

## Technical Operational Boundaries

1. **Single-Instance Database Lock**:
   - EduLedger ERP uses SQLite as its embedded database engine. It is designed for single-workstation desktop installation or shared network folder with single active writer. Multiple concurrent write instances across a network should avoid simultaneous receipt commits to prevent SQLite database busy locks.

2. **PDF Viewer Dependency**:
   - Built-in PDF receipt preview requires a PDF viewer application installed on the system (e.g., Adobe Acrobat Reader, Google Chrome, Microsoft Edge, or Foxit PDF) for direct system printing.

3. **High-DPI Display Scaling**:
   - The application automatically enables Qt High DPI scaling (`PassThrough` policy). On displays with >200% OS font scaling, standard Windows display setting adjustments may be recommended for optimal font rendering.
