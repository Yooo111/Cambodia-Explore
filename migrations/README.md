Run this one-time migration after renaming the model field from `CityName` to `ProvinceName`.

From project root:

```powershell
python migrations/rename_cityname_to_provincename.py
```

What it does:
- Checks `instance/urac_account.db`
- Renames `locations.CityName` to `locations.ProvinceName`
- Skips safely if already migrated

Rollback (if needed):

```powershell
python migrations/rollback_provincename_to_cityname.py
```

Rollback script:
- Checks `instance/urac_account.db`
- Renames `locations.ProvinceName` back to `locations.CityName`
- Skips safely if already in old schema
