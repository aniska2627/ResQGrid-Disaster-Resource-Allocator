# ResQGrid-Disaster-Resource-Allocator
A Python desktop application prototype for managing disaster incidents and allocating relief resources using transparent, rule-based recommendations.

## Features
- Disaster incident reporting and severity tracking
- Resource inventory management
- Smart resource allocation recommendations
- Allocation status tracking
- Dashboard statistics
- Local JSON data storage
- JSON export

## Technologies
- Python 3
- Tkinter and ttk
- JSON
- Python standard library

## How to Run
1. Install Python 3.
2. Download `resqgrid.py` from this repository.
3. Open it in Python IDLE.
4. Press F5 or select Run → Run Module.

Alternatively, run:

```bash
python resqgrid.py
```

## Smart Allocation
The matching score uses area, incident severity, disaster compatibility, available quantity, and an illustrative nearby-zone fallback.

This is a rule-based prototype, not a trained machine-learning model. The zone ordering is not real geographic distance.

## Data Storage
The application stores records locally in `resqgrid_data.json`.

## Limitations
- Desktop application, not a web application
- Demo data and local storage
- No live maps, weather feeds, or emergency-service integration
- Not intended for real-world emergency dispatch

## Screenshots
Add screenshots from the running application to the `screenshots/` folder.

## Future Improvements
- Database and multi-user support
- User authentication
- Real geographic distance calculations
- Verified data integrations
- Automated testing
