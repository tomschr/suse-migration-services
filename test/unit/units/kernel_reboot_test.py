from unittest.mock import (
    patch, call
)
from pytest import raises
from suse_migration_services.defaults import Defaults
from suse_migration_services.units.kernel_reboot import (
    main, _get_cmdline
)
from suse_migration_services.exceptions import (
    DistMigrationKernelRebootException
)


class TestKernelReboot(object):
    @patch('os.path.exists')
    def test_get_cmd_line_grub_cfg_not_present(self, mock_os_path_exists):
        mock_os_path_exists.return_value = False
        with raises(DistMigrationKernelRebootException):
            _get_cmdline(Defaults.get_grub_config_file())

    @patch('suse_migration_services.defaults.Defaults.get_grub_config_file')
    def test_get_cmd_line(
        self, mock_grub_path
    ):
        mock_grub_path.return_value = '../data/fake_grub.cfg'
        grub_cmd_content = \
            'root=UUID=ec7aaf92-30ea-4c07-991a-4700177ce1b8 ' + \
            'splash root=UUID=ec7aaf92-30ea-4c07-991a-4700177ce1b8 rw'
        result = _get_cmdline(Defaults.get_target_kernel())
        assert result == grub_cmd_content

    @patch('suse_migration_services.command.Command.run')
    @patch('suse_migration_services.units.kernel_reboot._get_cmdline')
    def test_main_raises_on_kernel_load(
            self, mock_get_cmdline, mock_Command_run
    ):
        cmd_line = \
            'root=UUID=ec7aaf92-30ea-4c07-991a-4700177ce1b8' + \
            'splash root=UUID=ec7aaf92-30ea-4c07-991a-4700177ce1b8 rw'
        mock_get_cmdline.return_value = cmd_line
        mock_Command_run.side_effect = [
            mock_Command_run.DEFAULT,
            mock_Command_run.DEFAULT,
            Exception,
            mock_Command_run.DEFAULT
        ]
        with raises(DistMigrationKernelRebootException):
            main()
        assert mock_Command_run.call_args_list == [
            call(
                ['kexec', '--unload']
            ),
            call(
                [
                    'kexec',
                    '--load', '/boot/vmlinuz',
                    '--initrd', '/boot/initrd',
                    '--command-line', cmd_line
                ]
            ),
            call(
                ['kexec', '--exec']
            ),
            call(
                ['kexec', '--unload']
            )
        ]

    @patch('suse_migration_services.command.Command.run')
    @patch('suse_migration_services.units.kernel_reboot._get_cmdline')
    def test_main(
            self, mock_get_cmdline, mock_Command_run
    ):
        cmd_line = \
            'root=UUID=ec7aaf92-30ea-4c07-991a-4700177ce1b8' + \
            'splash root=UUID=ec7aaf92-30ea-4c07-991a-4700177ce1b8 rw'
        mock_get_cmdline.return_value = cmd_line
        main()
        assert mock_Command_run.call_args_list == [
            call(
                ['kexec', '--unload']
            ),
            call(
                [
                    'kexec',
                    '--load', '/boot/vmlinuz',
                    '--initrd', '/boot/initrd',
                    '--command-line', cmd_line
                ]
            ),
            call(
                ['kexec', '--exec']
            )
        ]
